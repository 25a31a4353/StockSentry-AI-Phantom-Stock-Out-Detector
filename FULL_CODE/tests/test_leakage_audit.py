"""
StockSentry AI — Strict Point-in-Time Leakage Verification Suite
(FULL_CODE/tests/test_leakage_audit.py)
Mathematically proves zero future information leakage around key milestone dates:
- 2026-07-31
- 2026-08-15
- 2026-08-31
- 2026-09-02
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from FULL_CODE.pipeline.data_loader import load_timeseries_panel
from FULL_CODE.pipeline.features import (
    compute_zero_runs,
    compute_baseline_demand_rate,
    compute_dynamic_delisted_mask
)
from FULL_CODE.pipeline.predict import generate_ranked_predictions
from FULL_CODE.pipeline.config import DATA_DIR, BEST_PARAMS


@pytest.fixture(scope="module")
def full_panel():
    parquet_file = DATA_DIR / "daily_sales_inventory.parquet"
    if not parquet_file.exists():
        pytest.skip("Official competition daily_sales_inventory.parquet dataset not present in data/")
    return load_timeseries_panel(DATA_DIR)


class TestPointInTimeLeakageAudit:

    @pytest.mark.parametrize("target_date", [
        "2026-07-31",
        "2026-08-15",
        "2026-08-31",
        "2026-09-02"
    ])
    def test_truncated_dataset_exact_equivalence(self, full_panel, target_date):
        """
        Truncation Test:
        If we completely truncate the dataset so that no records after D-1 exist,
        the prediction output for day D MUST be 100% identical to running with the full panel.
        This proves zero lookahead leakage from D, D+1, or any future date.
        """
        dates, sales, onhand, promo, store, sku = full_panel
        d_target = pd.Timestamp(target_date)
        d_minus_1 = d_target - pd.Timedelta(days=1)

        cutoff_idx = int(np.searchsorted(dates.values, np.datetime64(d_minus_1))) + 1
        assert dates[cutoff_idx - 1] == d_minus_1

        # 1. Predictions using full panel
        run_full = compute_zero_runs(sales)
        rate_full = compute_baseline_demand_rate(sales, run_full)
        del_full = compute_dynamic_delisted_mask(sales, sku, recent_k=5, hist_span=28)

        preds_full = generate_ranked_predictions(
            dates=dates, store=store, sku=sku, onhand=onhand,
            run=run_full, rate=rate_full, promo=promo, delisted_mask=del_full,
            window=(target_date, target_date), params=BEST_PARAMS
        )

        # 2. Predictions using truncated panel (strictly up to D-1)
        dates_trunc = dates[:cutoff_idx]
        sales_trunc = sales[:cutoff_idx]
        onhand_trunc = onhand[:cutoff_idx]
        promo_trunc = promo[:cutoff_idx]

        run_trunc = compute_zero_runs(sales_trunc)
        rate_trunc = compute_baseline_demand_rate(sales_trunc, run_trunc)
        del_trunc = compute_dynamic_delisted_mask(sales_trunc, sku, recent_k=5, hist_span=28)

        preds_trunc = generate_ranked_predictions(
            dates=dates_trunc, store=store, sku=sku, onhand=onhand_trunc,
            run=run_trunc, rate=rate_trunc, promo=promo_trunc, delisted_mask=del_trunc,
            window=(target_date, target_date), params=BEST_PARAMS
        )

        # Assert equivalence
        assert len(preds_full) == len(preds_trunc), f"Mismatch in row count for {target_date}"
        assert (preds_full["store_id"].values == preds_trunc["store_id"].values).all(), "Store ordering mismatch"
        assert (preds_full["sku_id"].values == preds_trunc["sku_id"].values).all(), "SKU ordering mismatch"
        assert (preds_full["rank"].values == preds_trunc["rank"].values).all(), "Rank mismatch"
        np.testing.assert_allclose(
            preds_full["confidence"].values,
            preds_trunc["confidence"].values,
            atol=1e-5,
            err_msg=f"Confidence value leakage detected on {target_date}"
        )
        assert (preds_full["reason"].values == preds_trunc["reason"].values).all(), "Reason text mismatch"
        assert (preds_full["predicted_type"].values == preds_trunc["predicted_type"].values).all(), "Type mismatch"

    def test_truth_labels_not_imported_in_pipeline(self):
        """Verifies that features.py and predict.py do not import or access dev_truth or dev_labels."""
        import FULL_CODE.pipeline.features as f_mod
        import FULL_CODE.pipeline.predict as p_mod

        f_src = Path(f_mod.__file__).read_text(encoding="utf-8")
        p_src = Path(p_mod.__file__).read_text(encoding="utf-8")

        assert "dev_truth" not in f_src
        assert "dev_labels" not in f_src
        assert "dev_truth" not in p_src
        assert "dev_labels" not in p_src

