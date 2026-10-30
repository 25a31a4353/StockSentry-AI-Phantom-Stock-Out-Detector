"""
StockSentry AI — Comprehensive Unit & Integration Test Suite (FULL_CODE/tests/test_pipeline.py)
Tests feature calculations, ranking constraints, delisting filters, and submission schemas.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from FULL_CODE.pipeline.features import (
    compute_zero_runs,
    compute_baseline_demand_rate,
    compute_poisson_posterior,
    compute_dynamic_delisted_mask
)
from FULL_CODE.pipeline.predict import generate_ranked_predictions


class TestFeatureEngineering:

    def test_compute_zero_runs(self):
        # 5 days, 2 series
        sales = np.array([
            [2, 0],
            [1, 0],
            [0, 1],
            [0, 0],
            [0, 0]
        ], dtype=np.float32)
        runs = compute_zero_runs(sales)
        expected = np.array([
            [0, 1],
            [0, 2],
            [1, 0],
            [2, 1],
            [3, 2]
        ], dtype=np.int32)
        np.testing.assert_array_equal(runs, expected)

    def test_poisson_probability_monotonicity(self):
        # Higher expected missed volume should yield strictly higher posterior anomaly confidence
        rate = np.array([[1.0, 2.0, 4.0]])
        run = np.array([[3, 3, 3]])
        promo = np.array([[0, 0, 0]])
        p, vol = compute_poisson_posterior(rate, run, promo)
        assert p[0, 0] < p[0, 1] < p[0, 2], "Posterior must be strictly monotonic in expected volume"

    def test_dynamic_delisted_mask(self):
        # 40 days, 2 SKUs across 12 stores
        T = 45
        N = 24  # 12 stores x 2 SKUs
        sales = np.ones((T, N), dtype=np.float32) * 2.0
        sku = np.array(["SKU-DELISTED"] * 12 + ["SKU-ACTIVE"] * 12)
        
        # Cease all sales for SKU-DELISTED starting day 30
        sales[30:, :12] = 0.0

        mask = compute_dynamic_delisted_mask(sales, sku, recent_k=7, hist_span=14)
        # On day 25, neither is delisted
        assert not mask[25, 0]
        assert not mask[25, 12]
        # On day 38 (8 days of zero sales across all 12 stores), SKU-DELISTED should be masked
        assert mask[38, 0]
        # SKU-ACTIVE should never be masked
        assert not mask[38, 12]


class TestPredictionContract:

    def test_max_per_store_day_limit_and_uniqueness(self):
        # Mock dataset with 30 candidate SKUs in one store
        dates = pd.date_range("2026-06-01", periods=10, freq="D")
        T, N = 10, 30
        store = np.array(["STR-01"] * N)
        sku = np.array([f"SKU-{i:03d}" for i in range(N)])
        onhand = np.full((T, N), 10.0, dtype=np.float32)
        run = np.full((T, N), 5, dtype=np.int32)
        rate = np.full((T, N), 2.0, dtype=np.float32)
        promo = np.zeros((T, N), dtype=np.int8)
        delisted_mask = np.zeros((T, N), dtype=bool)

        preds = generate_ranked_predictions(
            dates=dates,
            store=store,
            sku=sku,
            onhand=onhand,
            run=run,
            rate=rate,
            promo=promo,
            delisted_mask=delisted_mask,
            window=("2026-06-05", "2026-06-08")
        )

        assert not preds.empty
        # Exactly at most 20 per store-day
        counts = preds.groupby(["date", "store_id"]).size()
        assert (counts <= 20).all()
        assert (counts == 20).all()

        # Ranks must be 1..20 strictly unique per store-day
        for (d, s), group in preds.groupby(["date", "store_id"]):
            ranks = group["rank"].tolist()
            assert ranks == list(range(1, len(ranks) + 1))
            assert group["sku_id"].nunique() == len(ranks)

    def test_as_of_truncated_dates_handling(self):
        # When dataset ends on 2026-09-15, predicting window 2026-09-03..2026-09-30
        # should gracefully output only up to 2026-09-16 without crashing
        dates = pd.date_range("2026-09-01", "2026-09-15", freq="D")
        T, N = len(dates), 2
        store = np.array(["STR-01", "STR-01"])
        sku = np.array(["SKU-01", "SKU-02"])
        onhand = np.full((T, N), 5.0, dtype=np.float32)
        run = np.full((T, N), 5, dtype=np.int32)
        rate = np.full((T, N), 1.0, dtype=np.float32)
        promo = np.zeros((T, N), dtype=np.int8)
        delisted_mask = np.zeros((T, N), dtype=bool)

        preds = generate_ranked_predictions(
            dates=dates, store=store, sku=sku, onhand=onhand,
            run=run, rate=rate, promo=promo, delisted_mask=delisted_mask,
            window=("2026-09-03", "2026-09-30")
        )
        assert not preds.empty
        max_date_generated = preds["date"].max()
        assert max_date_generated == "2026-09-16"
        # Dates 2026-09-17 through 2026-09-30 must be omitted because D-1 is not in historical data
        assert "2026-09-17" not in preds["date"].values
