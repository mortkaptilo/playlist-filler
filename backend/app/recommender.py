"""
Recommendation logic — three scoring methods + ensemble merge.

Each method returns a dict {track_id: raw_score} for its top candidates.
Scores are min-max normalised to [0, 1] before averaging so no single
method dominates due to scale differences.
"""

import numpy as np
import pandas as pd

from app.loader import ModelStore
from app.schemas import TrackResponse


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalise(scores: dict[str, float]) -> dict[str, float]:
    """Min-max normalise a score dict to [0, 1]."""
    if not scores:
        return {}
    vals = np.array(list(scores.values()), dtype=np.float32)
    lo, hi = vals.min(), vals.max()
    if hi == lo:
        return {k: 1.0 for k in scores}
    return {k: float((v - lo) / (hi - lo)) for k, v in scores.items()}


def _top_k_from_scores(
    scores: np.ndarray,
    id_list: list[str],
    seed_set: set[str],
    k: int,
) -> dict[str, float]:
    """Return the top-k {track_id: score} pairs, excluding seeds."""
    actual_k = min(k, len(scores))
    top_indices = np.argpartition(scores, -actual_k)[-actual_k:]
    top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]
    return {
        id_list[i]: float(scores[i])
        for i in top_indices
        if id_list[i] not in seed_set
    }


# ── Scoring methods ───────────────────────────────────────────────────────────

def _item_based(
    store: ModelStore, seed_ids: list[str], seed_set: set[str], k: int
) -> dict[str, float]:
    """
    Average the scaled audio-feature vectors of the seed tracks, then rank
    all tracks by cosine similarity to that centroid.
    """
    indices = [store.audio_feat_idx[tid] for tid in seed_ids if tid in store.audio_feat_idx]
    if not indices:
        return {}

    query = store.item_features_scaled[indices].mean(axis=0)
    norm = np.linalg.norm(query)
    if norm > 0:
        query /= norm

    # Rows are already L2-normalised → dot product == cosine similarity
    cosine_scores = store.item_features_scaled @ query   # (n_tracks,)

    # Zero out seeds
    for i in indices:
        cosine_scores[i] = -np.inf

    return _top_k_from_scores(cosine_scores, store.audio_feature_ids, seed_set, k)


def _user_based(
    store: ModelStore, seed_ids: list[str], seed_set: set[str], k: int
) -> dict[str, float]:
    """
    Build a virtual-user vector from the seed tracks, find the most similar
    real users via cosine similarity, then score tracks by their
    similarity-weighted popularity among those users.
    """
    indices = [store.ui_track_idx[tid] for tid in seed_ids if tid in store.ui_track_idx]
    if not indices:
        return {}

    n_items = store.user_item_norm.shape[1]
    virtual_user = np.zeros(n_items, dtype=np.float32)
    for i in indices:
        virtual_user[i] = 1.0
    norm = np.linalg.norm(virtual_user)
    if norm > 0:
        virtual_user /= norm

    # Cosine similarity between virtual user and every real user
    user_sims = store.user_item_norm.dot(virtual_user)           # (n_users,)

    # Aggregate: weighted sum of user listening vectors
    track_scores = np.asarray(
        store.user_item_norm.T.dot(user_sims)                    # (n_items,)
    ).flatten()

    for i in indices:
        track_scores[i] = -np.inf

    return _top_k_from_scores(track_scores, store.ui_track_ids, seed_set, k)


def _svd(
    store: ModelStore, seed_ids: list[str], seed_set: set[str], k: int
) -> dict[str, float]:
    """
    Project the virtual-user item vector into the SVD latent space, then
    score every track by its dot product with the projected query.

    Projection:  v_latent = virtual_user @ Vt.T          (1 × k)
    Scoring:     scores   = v_latent @ Vt                 (1 × n_items)
    """
    indices = [store.ui_track_idx[tid] for tid in seed_ids if tid in store.ui_track_idx]
    if not indices:
        return {}

    n_items = store.svd_Vt.shape[1]
    virtual_user = np.zeros(n_items, dtype=np.float32)
    for i in indices:
        virtual_user[i] = 1.0

    v_latent = virtual_user @ store.svd_Vt.T               # (k,)
    scores = (v_latent @ store.svd_Vt).astype(np.float32)  # (n_items,)

    for i in indices:
        scores[i] = -np.inf

    return _top_k_from_scores(scores, store.ui_track_ids, seed_set, k)


# ── Public API ────────────────────────────────────────────────────────────────

def recommend(
    store: ModelStore,
    seed_ids: list[str],
    top_n: int = 20,
) -> list[TrackResponse]:
    """
    Run all three models, normalise and average their scores, return the
    top-n recommended tracks with metadata.
    """
    # Filter to known track IDs
    known = {*store.audio_feat_idx, *store.ui_track_idx}
    valid_seeds = [tid for tid in seed_ids if tid in known]
    if not valid_seeds:
        return []

    seed_set = set(valid_seeds)
    candidates_k = top_n * 5   # fetch extra before merging

    raw = {
        "item":  _item_based(store, valid_seeds, seed_set, candidates_k),
        "user":  _user_based(store, valid_seeds, seed_set, candidates_k),
        "svd":   _svd(store,        valid_seeds, seed_set, candidates_k),
    }

    # Normalise each method's scores to [0, 1]
    normed = {method: _normalise(scores) for method, scores in raw.items()}

    # Average across whichever methods produced a score for each candidate
    all_candidates: set[str] = set().union(*normed.values())
    merged: dict[str, float] = {}
    for tid in all_candidates:
        method_scores = [normed[m][tid] for m in normed if tid in normed[m]]
        merged[tid] = sum(method_scores) / len(method_scores)

    # Sort and trim
    top_ids = sorted(merged, key=merged.__getitem__, reverse=True)[:top_n]

    # Build response objects
    results: list[TrackResponse] = []
    for tid in top_ids:
        if tid not in store.track_meta.index:
            continue
        row = store.track_meta.loc[tid]
        results.append(TrackResponse(
            track_id=tid,
            name=row["name"],
            artist=row["artist"],
            genre=row["genre"] if row["genre"] else None,
            year=int(row["year"]) if pd.notna(row["year"]) else None,
        ))

    return results
