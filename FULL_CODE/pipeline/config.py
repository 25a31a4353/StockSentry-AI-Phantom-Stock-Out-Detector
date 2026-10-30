"""
StockSentry AI — Configuration Module (FULL_CODE/pipeline/config.py)
Defines competition constants, schema definitions, parameter spaces, and paths.
"""

from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SUBMISSION_DIR = ROOT / "submission"
REPORTS_DIR = ROOT / "FULL_CODE" / "reports"
DOCS_DIR = ROOT / "FULL_CODE" / "docs"

# Official Competition Windows & Constraints
DEV_WINDOW = ("2026-06-04", "2026-09-02")
TEST_WINDOW = ("2026-09-03", "2026-09-30")
MAX_PER_STORE_DAY = 20
LOOKBACK_DAYS = 28
MIN_HISTORY_DAYS = 7

# Model Hyperparameters (Tuned on Store-Held-Out Validation)
BEST_PARAMS = {
    "n_min_run": 4,
    "p0": 0.03,
    "alpha": 0.85,
    "slow_penalty": 1.0,
    "slow_threshold": 0.25,
    "promo_multiplier": 0.20,
    "delisted_recent_k": 5,
    "delisted_hist_span": 28,
    "delisted_min_stores": 10,
    "delisted_min_hist_rate": 10.0
}

# Official Truth Labels
LABEL_TYPES = {
    "POSITIVE": {"phantom", "misplaced"},
    "DECOY": {"delisted"}
}

