#!/usr/bin/env python3
"""
StockSentry AI — Systematic Model Comparison & Validation Runner
Evaluates Model A (Baseline), Model B (Baseline + Delisted Filter),
Model C (Poisson Bayesian), Model D (Poisson + Promo/DOW), and Model E (Full Hybrid).
Outputs results to FULL_CODE/reports/experiment_results.csv and scores via official evaluate.py.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "FULL_CODE" / "reports"
SUBMISSION_DIR = ROOT / "submission"
DEV_WINDOW = ("2026-06-04", "2026-09-02")
K = 20
LOOKBACK = 28


def _codes(col: pd.Series):
    if isinstance(col.dtype, pd.CategoricalDtype):
        return col.cat.codes.to_numpy(), np.asarray(col.cat.categories, dtype=str)
    codes, uniq = pd.factorize(col, sort=True)
    return codes, np.asarray(uniq, dtype=str)


def load_all_data(data_dir: Path):
    print("[*] Loading full parquet dataset...")
    df = pd.read_parquet(
        data_dir / "daily_sales_inventory.parquet",
        columns=["date", "store_id", "sku_id", "units_sold", "on_hand_eod", "on_promo"]
    )
    dates = np.sort(df["date"].unique())
    t = np.searchsorted(dates, df["date"].to_numpy())
    st_c, st_u = _codes(df["store_id"])
    sk_c, sk_u = _codes(df["sku_id"])
    pair = st_c.astype(np.int64) * len(sk_u) + sk_c
    codes, uniq = pd.factorize(pair, sort=True)
    T, N = len(dates), len(uniq)

    sales = np.zeros((T, N), dtype=np.float32)
    onhand = np.full((T, N), np.nan, dtype=np.float32)
    promo = np.zeros((T, N), dtype=np.int8)

    sales[t, codes] = df["units_sold"].to_numpy(dtype=np.float32)
    onhand[t, codes] = df["on_hand_eod"].to_numpy(dtype=np.float32, na_value=np.nan)
    if "on_promo" in df.columns:
        promo[t, codes] = df["on_promo"].to_numpy(dtype=np.int8)

    del df, t, pair, codes
    onhand = pd.DataFrame(onhand).ffill().to_numpy(dtype=np.float32)
    store = st_u[uniq // len(sk_u)]
    sku = sk_u[uniq % len(sk_u)]
    return pd.DatetimeIndex(dates), sales, onhand, promo, store, sku


def build_base_signals(dates: pd.DatetimeIndex, sales: np.ndarray, promo: np.ndarray, sku: np.ndarray):
    T, N = sales.shape
    run = np.zeros((T, N), dtype=np.int32)
    r = np.zeros(N, dtype=np.int32)
    for t in range(T):
        r = np.where(sales[t] == 0, r + 1, 0)
        run[t] = r

    cs = np.vstack([np.zeros((1, N), np.float64), np.cumsum(sales, axis=0, dtype=np.float64)])
    rate = np.full((T, N), np.nan, dtype=np.float32)
    cols = np.arange(N)
    for t in range(T):
        s_idx = np.clip(t - run[t] + 1, 0, T)
        lo = np.clip(s_idx - LOOKBACK, 0, None)
        span = s_idx - lo
        rt = (cs[s_idx, cols] - cs[lo, cols]) / np.maximum(span, 1)
        rate[t] = np.where(span >= 7, rt, np.nan)

    # Dynamic point-in-time delisting detector
    # Evaluated at every day t using strictly data up to t
    print("[*] Computing point-in-time chain delisting mask...")
    unique_skus, sku_inverse = np.unique(sku, return_inverse=True)
    n_skus = len(unique_skus)
    
    # Precompute chain daily sales per SKU
    chain_sales = np.zeros((T, n_skus), dtype=np.float32)
    for i in range(N):
        chain_sales[:, sku_inverse[i]] += sales[:, i]

    # Precompute store counts per SKU
    store_counts = np.bincount(sku_inverse, minlength=n_skus)

    delisted_mask = np.zeros((T, N), dtype=bool)
    recent_k = 10
    hist_span = 28
    
    for t in range(recent_k + hist_span, T):
        recent_tot = np.sum(chain_sales[t - recent_k + 1:t + 1], axis=0)
        hist_avg = np.mean(chain_sales[t - recent_k - hist_span + 1:t - recent_k + 1], axis=0)
        is_del = (hist_avg >= 10.0) & (recent_tot == 0) & (store_counts >= 10)
        # Broadcast to series
        delisted_mask[t] = is_del[sku_inverse]

    return run, rate, delisted_mask


def generate_dev_submission(dates, store, sku, onhand, run, rate, promo, delisted_mask,
                            model_type="baseline", n_min_run=7, p0=0.03, alpha=1.0, slow_pen=1.0, promo_weight=0.0):
    out = []
    stores = np.unique(store)
    
    for D in pd.date_range(*DEV_WINDOW, freq="D"):
        t = int(np.searchsorted(dates.values, np.datetime64(D - pd.Timedelta(days=1))))
        if t >= len(dates) or dates[t] != D - pd.Timedelta(days=1):
            continue
        t = min(t, len(dates) - 1)

        exp_vol = rate[t] * run[t]
        
        if model_type == "baseline":
            score = exp_vol
            ok = (run[t] >= n_min_run) & (onhand[t] > 0) & np.isfinite(score) & (score > 0)
        elif model_type == "baseline_delisted":
            score = exp_vol
            ok = (run[t] >= n_min_run) & (onhand[t] > 0) & np.isfinite(score) & (score > 0) & (~delisted_mask[t])
        elif model_type == "poisson_bayesian":
            odds = (1.0 - p0) / p0
            p_phantom = 1.0 / (1.0 + odds * np.exp(-np.clip(exp_vol, 0, 30)))
            score = p_phantom * (exp_vol ** alpha)
            ok = (run[t] >= n_min_run) & (onhand[t] > 0) & np.isfinite(score) & (score > 0) & (~delisted_mask[t])
        elif model_type == "poisson_dow_promo":
            promo_mult = 1.0 + promo_weight * promo[t]
            adj_vol = exp_vol * promo_mult
            odds = (1.0 - p0) / p0
            p_phantom = 1.0 / (1.0 + odds * np.exp(-np.clip(adj_vol, 0, 30)))
            score = p_phantom * (adj_vol ** alpha)
            ok = (run[t] >= n_min_run) & (onhand[t] > 0) & np.isfinite(score) & (score > 0) & (~delisted_mask[t])
        elif model_type == "stocksentry_hybrid":
            promo_mult = 1.0 + promo_weight * promo[t]
            adj_vol = exp_vol * promo_mult
            odds = (1.0 - p0) / p0
            p_phantom = 1.0 / (1.0 + odds * np.exp(-np.clip(adj_vol, 0, 30)))
            # Slow mover filter
            slow_penalty = np.where(rate[t] < 0.25, slow_pen, 1.0)
            # On-hand depth factor (higher confidence if ERP claims multi-unit stock)
            onhand_factor = np.clip(np.log1p(np.maximum(0, onhand[t])), 1.0, 3.0) ** 0.25
            score = p_phantom * (adj_vol ** alpha) * slow_penalty * onhand_factor
            ok = (run[t] >= n_min_run) & (onhand[t] > 0) & np.isfinite(score) & (score > 0) & (~delisted_mask[t])
        else:
            raise ValueError(f"Unknown model_type {model_type}")

        for s in stores:
            idx = np.where(ok & (store == s))[0]
            if len(idx) == 0:
                continue
            top = idx[np.argsort(-score[idx], kind="stable")[:K]]
            sc = score[top]
            
            # Stretch type classification
            pred_types = []
            for i in top:
                if onhand[t, i] >= 4 and run[t, i] >= 4:
                    pred_types.append("phantom")
                else:
                    pred_types.append("misplaced")

            out.append(pd.DataFrame({
                "date": D.strftime("%Y-%m-%d"),
                "store_id": s,
                "sku_id": sku[top],
                "rank": np.arange(1, len(top) + 1),
                "confidence": np.round(1 - np.exp(-np.clip(sc, 0, 25)), 4),
                "reason": [
                    f"Zero sales for {int(run[t, i])} days vs system on-hand {int(onhand[t, i])}; "
                    f"baseline velocity {rate[t, i]:.1f}/day" for i in top
                ],
                "predicted_type": pred_types
            }))

    cols = ["date", "store_id", "sku_id", "rank", "confidence", "reason", "predicted_type"]
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=cols)


def evaluate_preds(sub_df: pd.DataFrame, truth_path: Path):
    tmp_sub = SUBMISSION_DIR / "_temp_eval.csv"
    tmp_out = REPORTS_DIR / "_temp_score.json"
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    sub_df.to_csv(tmp_sub, index=False)

    eval_script = ROOT / "evaluate.py"
    cmd = [
        sys.executable, str(eval_script),
        "--submission", str(tmp_sub),
        "--truth", str(truth_path),
        "--out", str(tmp_out)
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    with open(tmp_out, "r", encoding="utf-8") as f:
        res = json.load(f)
    if tmp_sub.exists():
        tmp_sub.unlink()
    if tmp_out.exists():
        tmp_out.unlink()
    return res


def main():
    dates, sales, onhand, promo, store, sku = load_all_data(DATA_DIR)
    run, rate, delisted_mask = build_base_signals(dates, sales, promo, sku)
    truth_path = DATA_DIR / "dev_truth.csv"

    experiments = [
        {"name": "Model A (Organizer Baseline)", "type": "baseline", "n": 7, "p0": 0.03, "alpha": 1.0, "slow_pen": 1.0, "promo": 0.0},
        {"name": "Model B (Baseline + Delisted Filter)", "type": "baseline_delisted", "n": 7, "p0": 0.03, "alpha": 1.0, "slow_pen": 1.0, "promo": 0.0},
        {"name": "Model B2 (Delisted Filter N=5)", "type": "baseline_delisted", "n": 5, "p0": 0.03, "alpha": 1.0, "slow_pen": 1.0, "promo": 0.0},
        {"name": "Model B3 (Delisted Filter N=4)", "type": "baseline_delisted", "n": 4, "p0": 0.03, "alpha": 1.0, "slow_pen": 1.0, "promo": 0.0},
        {"name": "Model C (Poisson Bayesian N=4)", "type": "poisson_bayesian", "n": 4, "p0": 0.03, "alpha": 0.85, "slow_pen": 1.0, "promo": 0.0},
        {"name": "Model D (Poisson + Promo N=4)", "type": "poisson_dow_promo", "n": 4, "p0": 0.03, "alpha": 0.85, "slow_pen": 1.0, "promo": 0.30},
        {"name": "Model E (StockSentry Hybrid N=4)", "type": "stocksentry_hybrid", "n": 4, "p0": 0.03, "alpha": 0.85, "slow_pen": 0.45, "promo": 0.30},
        {"name": "Model E2 (StockSentry Hybrid N=3)", "type": "stocksentry_hybrid", "n": 3, "p0": 0.03, "alpha": 0.85, "slow_pen": 0.45, "promo": 0.30},
        {"name": "Model E3 (StockSentry Hybrid N=5)", "type": "stocksentry_hybrid", "n": 5, "p0": 0.03, "alpha": 0.85, "slow_pen": 0.45, "promo": 0.30},
    ]

    results = []
    print("\n" + "=" * 90)
    print(f"{'Experiment Name':<35} | {'P@20':<8} | {'Ceiling':<8} | {'RowRec':<8} | {'EpsRec':<8} | {'Delisted%':<10} | {'TypeAcc':<8}")
    print("=" * 90)

    for exp in experiments:
        t0 = time.time()
        sub = generate_dev_submission(
            dates, store, sku, onhand, run, rate, promo, delisted_mask,
            model_type=exp["type"], n_min_run=exp["n"], p0=exp["p0"],
            alpha=exp["alpha"], slow_pen=exp["slow_pen"], promo_weight=exp["promo"]
        )
        res = evaluate_preds(sub, truth_path)
        runtime = time.time() - t0
        
        row = {
            "experiment_name": exp["name"],
            "model_type": exp["type"],
            "n_min_run": exp["n"],
            "p0": exp["p0"],
            "alpha": exp["alpha"],
            "slow_pen": exp["slow_pen"],
            "promo_weight": exp["promo"],
            "precision_at_20": res["primary_score"],
            "ceiling_precision_at_20": res["ceiling_precision_at_20"],
            "share_of_ceiling": res["primary_score_as_share_of_ceiling"],
            "row_recall": res["row_recall"],
            "episode_recall": res["episode_recall"],
            "share_of_flags_on_delisted": res["share_of_flags_on_delisted_decoys"],
            "type_accuracy": res.get("type_accuracy"),
            "n_hits": res["n_hits"],
            "runtime_seconds": round(runtime, 2)
        }
        results.append(row)
        print(f"{exp['name']:<35} | {row['precision_at_20']:.4f}   | {row['ceiling_precision_at_20']:.4f}   | "
              f"{row['row_recall']:.4f}   | {row['episode_recall']:.4f}   | {row['share_of_flags_on_delisted']:.4f}     | "
              f"{row['type_accuracy'] if row['type_accuracy'] else 0.0:.4f}")

    # Save to CSV
    csv_file = REPORTS_DIR / "experiment_results.csv"
    pd.DataFrame(results).to_csv(csv_file, index=False)
    print("=" * 90)
    print(f"[+] All experiment results saved to: {csv_file}")


if __name__ == "__main__":
    main()

