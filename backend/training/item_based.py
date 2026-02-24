"""
Item-based cosine similarity model.

Reads:
  models/audio_features.npy
  models/audio_feature_ids.pkl

Writes:
  models/item_features_scaled.npy   StandardScaler-normalized feature matrix
  models/item_scaler.pkl            Fitted StandardScaler (needed at inference)

At inference the API will:
  1. Build a query vector by averaging the scaled feature rows of the seed tracks.
  2. Compute cosine similarity between the query and every row in item_features_scaled.
  3. Return the top-N most similar tracks (excluding the seeds themselves).
"""

import logging
import pickle

import numpy as np
from sklearn.preprocessing import StandardScaler

from training.config import MODELS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def run() -> None:
    # ── Load raw audio features ────────────────────────────────────────────
    log.info("Loading audio_features.npy …")
    features: np.ndarray = np.load(MODELS_DIR / "audio_features.npy")
    log.info("  shape=%s  dtype=%s", features.shape, features.dtype)

    # ── Fit and apply StandardScaler ──────────────────────────────────────
    # Each feature is brought to zero mean and unit variance so that
    # dimensions with large absolute ranges (e.g. loudness, tempo) don't
    # dominate the cosine distance.
    scaler = StandardScaler()
    scaled: np.ndarray = scaler.fit_transform(features).astype(np.float32)

    # L2-normalise every row so that cosine similarity == dot product.
    # This lets inference use a single matrix-vector multiply instead of
    # the full cosine formula.
    norms = np.linalg.norm(scaled, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)   # avoid division by zero
    scaled /= norms

    # ── Persist ────────────────────────────────────────────────────────────
    np.save(MODELS_DIR / "item_features_scaled.npy", scaled)
    with open(MODELS_DIR / "item_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    log.info("Saved item_features_scaled.npy  shape=%s", scaled.shape)
    log.info("Saved item_scaler.pkl")
    log.info("Item-based model done.")


if __name__ == "__main__":
    run()
