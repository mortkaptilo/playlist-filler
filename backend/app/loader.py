"""
Loads all trained model artifacts from disk into a ModelStore.
Called once at API startup via FastAPI's lifespan context.
"""

import logging
import pickle
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, load_npz

from training.config import MODELS_DIR

log = logging.getLogger(__name__)


@dataclass
class ModelStore:
    # Track metadata (indexed by track_id)
    track_meta: pd.DataFrame

    # Item-based cosine similarity
    audio_feature_ids: list[str]
    audio_feat_idx: dict[str, int]
    item_features_scaled: np.ndarray       # (n_tracks × 12), L2-normalised rows

    # User-based cosine similarity
    ui_track_ids: list[str]
    ui_track_idx: dict[str, int]
    user_item_norm: csr_matrix             # (n_users × n_items), L2-normalised rows

    # SVD
    svd_Vt: np.ndarray                    # (k × n_items)
    svd_singular_values: np.ndarray       # (k,)


def _pkl(name: str):
    with open(MODELS_DIR / name, "rb") as f:
        return pickle.load(f)


def load_models() -> ModelStore:
    t0 = time.perf_counter()
    log.info("Loading model artifacts from %s …", MODELS_DIR)

    track_meta: pd.DataFrame = _pkl("track_meta.pkl")

    audio_feature_ids: list[str] = _pkl("audio_feature_ids.pkl")
    audio_feat_idx = {tid: i for i, tid in enumerate(audio_feature_ids)}
    item_features_scaled: np.ndarray = np.load(MODELS_DIR / "item_features_scaled.npy")

    ui_track_ids: list[str] = _pkl("ui_track_ids.pkl")
    ui_track_idx = {tid: i for i, tid in enumerate(ui_track_ids)}
    user_item_norm: csr_matrix = load_npz(MODELS_DIR / "user_item_norm.npz")

    svd_Vt: np.ndarray = np.load(MODELS_DIR / "svd_Vt.npy")
    svd_singular_values: np.ndarray = np.load(MODELS_DIR / "svd_singular_values.npy")

    store = ModelStore(
        track_meta=track_meta,
        audio_feature_ids=audio_feature_ids,
        audio_feat_idx=audio_feat_idx,
        item_features_scaled=item_features_scaled,
        ui_track_ids=ui_track_ids,
        ui_track_idx=ui_track_idx,
        user_item_norm=user_item_norm,
        svd_Vt=svd_Vt,
        svd_singular_values=svd_singular_values,
    )

    log.info(
        "Models loaded in %.2fs  |  tracks=%d  users=%d  svd_k=%d",
        time.perf_counter() - t0,
        len(track_meta),
        user_item_norm.shape[0],
        svd_Vt.shape[0],
    )
    return store
