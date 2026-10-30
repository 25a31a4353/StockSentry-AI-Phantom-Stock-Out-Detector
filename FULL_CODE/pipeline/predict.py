"""
StockSentry AI — Official Submission Prediction Generator (FULL_CODE/pipeline/predict.py)
Generates valid daily Top-20 ranking predictions strictly adhering to the competition contract.
"""

from __future__ import annotations

from typing import Tuple, List
import numpy as np
import pandas as pd

from .config import MAX_PER_STORE_DAY, BEST_PARAMS


def generate_ranked_predictions(
    dates: pd.DatetimeIndex,
    store: np.ndarray,
    sku: np.ndarray,
    onhand: np.ndarray,
    run: np.ndarray,
    rate: np.ndarray,
    promo: np.ndarray,
    delisted_mask: np.ndarray,
    window: Tuple[str, str],
    params: dict = BEST_PARAMS,
    store_filter: List[str] = None
) -> pd.DataFrame:
    """
    Constructs the daily Top-20 verification queue for each store and day in window:
    - Enforces no-lookahead rule: Day D uses data up to D-1.
    - Limits to at most MAX_PER_STORE_DAY (20) per store-day.
    - Suppresses chain-wide delisted decoys point-in-time.
    - Classifies stretch predicted_type (phantom vs misplaced).
    """
    n_min_run = params.get("n_min_run", 4)
    p0 = params.get("p0", 0.03)
    alpha = params.get("alpha", 0.85)
    promo_weight = params.get("promo_multiplier", 0.35)
    slow_threshold = params.get("slow_threshold", 0.25)
    slow_penalty_val = params.get("slow_penalty", 0.45)

    all_stores = np.unique(store)
    target_stores = [s for s in all_stores if store_filter is None or s in store_filter]

    out = []

    for D in pd.date_range(*window, freq="D"):
        # List for day D is constructed strictly from data up to D-1
        t = int(np.searchsorted(dates.values, np.datetime64(D - pd.Timedelta(days=1))))
        if t >= len(dates) or dates[t] != D - pd.Timedelta(days=1):
            continue  # D-1 not in historical panel (e.g. as-of slice)
        t = min(t, len(dates) - 1)

        exp_vol = rate[t] * run[t]
        promo_mult = 1.0 + promo_weight * promo[t]
        adj_vol = exp_vol * promo_mult

        odds = (1.0 - p0) / p0
        p_phantom = 1.0 / (1.0 + odds * np.exp(-np.clip(adj_vol, 0, 30)))

        # Composite score
        score = p_phantom * (adj_vol ** alpha)

        # Validity mask: run >= N, system on-hand > 0, finite positive score, not delisted
        ok = (run[t] >= n_min_run) & (onhand[t] > 0) & np.isfinite(score) & (score > 0) & (~delisted_mask[t])

        for s in target_stores:
            idx = np.where(ok & (store == s))[0]
            if len(idx) == 0:
                continue

            # Rank top candidates (at most 20)
            top = idx[np.argsort(-score[idx], kind="stable")[:MAX_PER_STORE_DAY]]
            k_cand = len(top)

            # Stretch multi-class classification
            pred_types = []
            for i in top:
                if onhand[t, i] >= 4 and run[t, i] >= 4:
                    pred_types.append("phantom")
                else:
                    pred_types.append("misplaced")

            conf = np.round(np.clip(p_phantom[top], 0.30, 0.99), 4)

            out.append(pd.DataFrame({
                "date": D.strftime("%Y-%m-%d"),
                "store_id": s,
                "sku_id": sku[top],
                "rank": np.arange(1, k_cand + 1),
                "confidence": conf,
                "reason": [
                    f"Zero sales for {int(run[t, i])} days while system records {int(onhand[t, i])} on hand; "
                    f"expected velocity is {rate[t, i]:.1f}/day" for i in top
                ],
                "predicted_type": pred_types
            }))

    cols = ["date", "store_id", "sku_id", "rank", "confidence", "reason", "predicted_type"]
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=cols)

