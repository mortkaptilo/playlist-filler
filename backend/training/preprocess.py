"""
Preprocess raw CSVs into shared model-ready artifacts.

Outputs written to models/:
  track_meta.pkl          DataFrame(track_id, name, artist, genre, year)
  audio_features.npy      float32 ndarray (n_tracks × 12) — item-based features
  audio_feature_ids.pkl   list[str] of track_ids aligned with audio_features rows
  user_item.npz           scipy sparse CSR (n_users × n_items) — raw playcounts
  ui_track_ids.pkl        list[str] — column index for user_item
  ui_user_ids.pkl         list[str] — row index for user_item
"""

import logging
import pickle

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from training.config import (
    AUDIO_FEATURES,
    MAX_USERS,
    MODELS_DIR,
    MUSIC_INFO_CSV,
    USER_HISTORY_CSV,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def run() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Load music metadata ─────────────────────────────────────────────
    log.info("Loading music_info.csv …")
    music = pd.read_csv(
        MUSIC_INFO_CSV,
        usecols=["track_id", "name", "artist", "genre", "year"] + AUDIO_FEATURES,
        dtype={"track_id": str},
    )
    log.info("  %d tracks loaded", len(music))

    # Drop rows missing any audio feature
    before = len(music)
    music = music.dropna(subset=AUDIO_FEATURES)
    log.info("  %d tracks kept after dropping NaN audio features (dropped %d)", len(music), before - len(music))

    # ── 2. Load user listening history ────────────────────────────────────
    log.info("Loading user_listening_history.csv …")
    history = pd.read_csv(
        USER_HISTORY_CSV,
        dtype={"track_id": str, "user_id": str, "playcount": np.int32},
    )
    log.info("  %d interactions loaded", len(history))

    if MAX_USERS is not None:
        sampled_users = history["user_id"].drop_duplicates().sample(
            min(MAX_USERS, history["user_id"].nunique()), random_state=42
        )
        history = history[history["user_id"].isin(sampled_users)]
        log.info("  Subsampled to %d users → %d interactions", MAX_USERS, len(history))

    # ── 3. Align: keep only tracks present in both datasets ───────────────
    music_track_ids = set(music["track_id"])
    history_track_ids = set(history["track_id"])
    common = music_track_ids & history_track_ids

    log.info(
        "Track overlap: %d / %d music-info, %d / %d history",
        len(common), len(music_track_ids),
        len(common), len(history_track_ids),
    )

    music = music[music["track_id"].isin(common)].reset_index(drop=True)
    history = history[history["track_id"].isin(common)].reset_index(drop=True)

    # ── 4. Save track metadata ────────────────────────────────────────────
    track_meta = music[["track_id", "name", "artist", "genre", "year"]].copy()
    track_meta["genre"] = track_meta["genre"].fillna("")
    track_meta = track_meta.set_index("track_id")

    with open(MODELS_DIR / "track_meta.pkl", "wb") as f:
        pickle.dump(track_meta, f)
    log.info("Saved track_meta.pkl  (%d tracks)", len(track_meta))

    # ── 5. Save audio feature matrix ──────────────────────────────────────
    audio_feature_ids = music["track_id"].tolist()
    audio_features = music[AUDIO_FEATURES].to_numpy(dtype=np.float32)

    np.save(MODELS_DIR / "audio_features.npy", audio_features)
    with open(MODELS_DIR / "audio_feature_ids.pkl", "wb") as f:
        pickle.dump(audio_feature_ids, f)
    log.info("Saved audio_features.npy  shape=%s", audio_features.shape)

    # ── 6. Build and save sparse user-item matrix ─────────────────────────
    unique_users = history["user_id"].unique().tolist()
    unique_tracks = history["track_id"].unique().tolist()

    user_idx = {uid: i for i, uid in enumerate(unique_users)}
    track_idx = {tid: i for i, tid in enumerate(unique_tracks)}

    rows = history["user_id"].map(user_idx).to_numpy(dtype=np.int32)
    cols = history["track_id"].map(track_idx).to_numpy(dtype=np.int32)
    data = history["playcount"].to_numpy(dtype=np.float32)

    user_item = csr_matrix(
        (data, (rows, cols)),
        shape=(len(unique_users), len(unique_tracks)),
    )

    from scipy.sparse import save_npz
    save_npz(MODELS_DIR / "user_item.npz", user_item)
    with open(MODELS_DIR / "ui_track_ids.pkl", "wb") as f:
        pickle.dump(unique_tracks, f)
    with open(MODELS_DIR / "ui_user_ids.pkl", "wb") as f:
        pickle.dump(unique_users, f)

    log.info(
        "Saved user_item.npz  shape=%s  nnz=%d  density=%.4f%%",
        user_item.shape,
        user_item.nnz,
        100 * user_item.nnz / (user_item.shape[0] * user_item.shape[1]),
    )
    log.info("Preprocessing done.")


if __name__ == "__main__":
    run()
