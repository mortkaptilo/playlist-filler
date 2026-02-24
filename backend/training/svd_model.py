"""
SVD (matrix factorisation) model via TruncatedSVD.

Reads:
  models/user_item.npz

Writes:
  models/svd_Vt.npy               Item factors  — shape (k, n_items)
  models/svd_singular_values.npy  Singular values — shape (k,)

How it works
------------
TruncatedSVD decomposes  A ≈ U · diag(σ) · Vt  where:
  U    (n_users × k)  — user latent factors
  σ    (k,)           — singular values
  Vt   (k × n_items)  — item latent factors  ← saved here

At inference the API will:
  1. Build a virtual-user item vector v (1 × n_items) with 1s at seed columns.
  2. Project to latent space:  v_latent = v · Vt.T / σ   (shape: 1 × k)
  3. Score all items:          scores   = v_latent · Vt   (shape: 1 × n_items)
  4. Return top-N items by score (excluding the seeds).
"""

import logging
import pickle

import numpy as np
from scipy.sparse import load_npz
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

from training.config import MODELS_DIR, SVD_N_COMPONENTS, SVD_RANDOM_STATE

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def run() -> None:
    # ── Load user-item matrix ──────────────────────────────────────────────
    log.info("Loading user_item.npz …")
    user_item = load_npz(MODELS_DIR / "user_item.npz").astype(np.float32)
    log.info("  shape=%s  nnz=%d", user_item.shape, user_item.nnz)

    # ── Log1p-compress playcounts (same transform as user-based model) ─────
    user_item.data = np.log1p(user_item.data)

    # ── Fit TruncatedSVD ───────────────────────────────────────────────────
    log.info("Fitting TruncatedSVD  (n_components=%d) …", SVD_N_COMPONENTS)
    svd = TruncatedSVD(n_components=SVD_N_COMPONENTS, random_state=SVD_RANDOM_STATE)
    svd.fit(user_item)

    explained = svd.explained_variance_ratio_.sum()
    log.info("  Explained variance ratio: %.2f%%", 100 * explained)

    # ── Persist item factors and singular values ───────────────────────────
    # Vt rows are already unit-length after TruncatedSVD, but we normalise
    # explicitly to guard against numerical drift.
    Vt: np.ndarray = normalize(svd.components_, norm="l2").astype(np.float32)

    np.save(MODELS_DIR / "svd_Vt.npy", Vt)
    np.save(MODELS_DIR / "svd_singular_values.npy", svd.singular_values_.astype(np.float32))

    # Save the fitted SVD object so the API can reuse it if needed
    with open(MODELS_DIR / "svd_model.pkl", "wb") as f:
        pickle.dump(svd, f)

    log.info("Saved svd_Vt.npy              shape=%s", Vt.shape)
    log.info("Saved svd_singular_values.npy shape=%s", svd.singular_values_.shape)
    log.info("SVD model done.")


if __name__ == "__main__":
    run()
