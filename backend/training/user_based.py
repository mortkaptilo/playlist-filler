"""
User-based cosine similarity model.

Reads:
  models/user_item.npz

Writes:
  models/user_item_norm.npz   Log1p-transformed, L2-normalised user vectors
                              (sparse CSR, same shape as user_item.npz)

At inference the API will:
  1. Build a virtual-user vector: a sparse row with 1s at the seed-track columns.
  2. L2-normalise it (same transform as stored rows).
  3. Compute cosine similarity as dot products against every row in user_item_norm.
  4. Weight each candidate track by the similarity of the users who listened to it.
  5. Return the top-N highest-scored tracks (excluding the seeds).
"""

import logging

import numpy as np
from scipy.sparse import csr_matrix, load_npz, save_npz
from sklearn.preprocessing import normalize

from training.config import MODELS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def run() -> None:
    # ── Load raw user-item matrix ──────────────────────────────────────────
    log.info("Loading user_item.npz …")
    user_item: csr_matrix = load_npz(MODELS_DIR / "user_item.npz")
    log.info("  shape=%s  nnz=%d", user_item.shape, user_item.nnz)

    # ── Log1p-compress playcounts ──────────────────────────────────────────
    # Listening counts follow a heavy-tailed distribution; log1p brings
    # repeat-play signal into a reasonable range without discarding it.
    user_item = user_item.astype(np.float32)
    user_item.data = np.log1p(user_item.data)

    # ── L2-normalise each user row ─────────────────────────────────────────
    # After normalisation, cosine similarity between two users is just the
    # dot product of their rows — cheap at inference time.
    user_item_norm: csr_matrix = normalize(user_item, norm="l2", copy=True)

    # ── Persist ────────────────────────────────────────────────────────────
    save_npz(MODELS_DIR / "user_item_norm.npz", user_item_norm)
    log.info("Saved user_item_norm.npz  shape=%s", user_item_norm.shape)
    log.info("User-based model done.")


if __name__ == "__main__":
    run()
