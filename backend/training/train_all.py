"""
Full training pipeline — runs all steps in order.

Usage (from backend/):
    python -m training.train_all              # use full dataset
    python -m training.train_all --max-users 50000   # subsample users
"""

import argparse
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def _step(name: str, fn) -> None:
    log.info("=" * 60)
    log.info("STEP: %s", name)
    log.info("=" * 60)
    t0 = time.perf_counter()
    fn()
    elapsed = time.perf_counter() - t0
    log.info("  done in %.1fs\n", elapsed)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-users",
        type=int,
        default=None,
        help="Subsample this many users from the history CSV (default: all)",
    )
    args = parser.parse_args()

    # Patch config before importing the training modules so every module
    # sees the same value.
    import training.config as cfg
    if args.max_users is not None:
        cfg.MAX_USERS = args.max_users
        log.info("MAX_USERS set to %d", cfg.MAX_USERS)

    from training import preprocess, item_based, user_based, svd_model

    t_total = time.perf_counter()

    _step("Preprocessing", preprocess.run)
    _step("Item-based cosine similarity", item_based.run)
    _step("User-based cosine similarity", user_based.run)
    _step("SVD matrix factorisation", svd_model.run)

    total = time.perf_counter() - t_total
    log.info("=" * 60)
    log.info("ALL STEPS COMPLETE  (total %.1fs)", total)
    log.info("Model artifacts saved to:  %s", cfg.MODELS_DIR)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
