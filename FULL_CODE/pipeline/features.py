"""
StockSentry AI — Point-in-Time Feature Engineering Module (FULL_CODE/pipeline/features.py)
Constructs time-safe features strictly using information available as of day D-1.
Guarantees NO lookahead leakage.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Tuple

from .config import LOOKBACK_DAYS, MIN_HISTORY_DAYS


def compute_zero_runs(sales: np.ndarray) -> np.ndarray:
    """
    Computes running zero-sales streak up to day t:
    run[t, i] = number of consecutive days ending at day t with sales == 0.
    """
    T, N = sales.shape
    run = np.zeros((T, N), dtype=np.int32)
    r = np.zeros(N, dtype=np.int32)
    for t in range(T):
        r = np.where(sales[t] == 0, r + 1, 0)
        run[t] = r
    return run


def compute_baseline_demand_rate(sales: np.ndarray, run: np.ndarray, lookback: int = LOOKBACK_DAYS) -> np.ndarray:
    """
    Computes average daily units sold in the lookback window strictly BEFORE the current zero streak began.
    Prevents the anomaly itself from depressing its own demand baseline.
    """
    T, N = sales.shape
    cs = np.vstack([np.zeros((1, N), np.float64), np.cumsum(sales, axis=0, dtype=np.float64)])
    rate = np.full((T, N), np.nan, dtype=np.float32)
    cols = np.arange(N)

    for t in range(T):
        s_idx = np.clip(t - run[t] + 1, 0, T)
        lo = np.clip(s_idx - lookback, 0, None)
        span = s_idx - lo
        rt = (cs[s_idx, cols] - cs[lo, cols]) / np.maximum(span, 1)
        rate[t] = np.where(span >= MIN_HISTORY_DAYS, rt, np.nan)

    return rate


def compute_dynamic_delisted_mask(sales: np.ndarray, sku: np.ndarray, recent_k: int = 7, hist_span: int = 28) -> np.ndarray:
    """
    Point-in-time chain-wide delisting detector:
    Identifies if an SKU ceased selling across all stores in the chain for >= recent_k days
    after having had robust historical chain sales (>= 10 units/day across >= 10 stores).
    Evaluated strictly at day t using historical data up to day t. Zero future lookahead.
    """
    T, N = sales.shape
    unique_skus, sku_inverse = np.unique(sku, return_inverse=True)
    n_skus = len(unique_skus)

    # Precompute daily chain sales per SKU
    chain_sales = np.zeros((T, n_skus), dtype=np.float32)
    for i in range(N):
        chain_sales[:, sku_inverse[i]] += sales[:, i]

    store_counts = np.bincount(sku_inverse, minlength=n_skus)
    delisted_mask = np.zeros((T, N), dtype=bool)

    for t in range(recent_k + hist_span, T):
        recent_tot = np.sum(chain_sales[t - recent_k + 1:t + 1], axis=0)
        hist_avg = np.mean(chain_sales[t - recent_k - hist_span + 1:t - recent_k + 1], axis=0)
        is_del = (hist_avg >= 10.0) & (recent_tot == 0) & (store_counts >= 10)
        delisted_mask[t] = is_del[sku_inverse]

    return delisted_mask


def compute_poisson_posterior(rate: np.ndarray, run: np.ndarray, promo: np.ndarray, p0: float = 0.03, promo_mult: float = 0.35) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes Bayesian posterior probability P(Phantom | 0 sales for k days):
    Likelihood ratio under Poisson demand: exp(-expected_missed_volume).
    """
    promo_factor = 1.0 + promo_mult * promo
    exp_vol = rate * run * promo_factor
    odds = (1.0 - p0) / p0
    p_phantom = 1.0 / (1.0 + odds * np.exp(-np.clip(exp_vol, 0, 30)))
    return p_phantom, exp_vol

