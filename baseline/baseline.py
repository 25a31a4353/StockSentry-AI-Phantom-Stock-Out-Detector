#!/usr/bin/env python3
"""R1 baseline -- "zero-sales run" rule.

The list for day D is built from data up to and including D-1 (what the store knows before opening on D).
For every store and SKU, as of the end of day D-1:
    run      = number of consecutive days (ending D-1) with units_sold == 0
    rate     = average daily units sold in the 28 days BEFORE the run started
    score    = rate x run          (= the number of sales we "should" have seen by now)
and flag the SKU only if run >= N_MIN_RUN and the system still shows stock (on_hand_eod > 0 on D-1).
The 20 highest scores per store form the "go check this shelf" list for day D.

Usage (from the package root):
    python baseline/baseline.py                 # writes dev + test predictions
    python baseline/baseline.py --n-min-run 10  # try a different N
Outputs:
    submission/R1_predictions.csv       test window 2026-09-03..2026-09-30 (this is what you submit)
    submission/R1_predictions_dev.csv   dev window  2026-06-04..2026-09-02 (score it with data/dev_truth.csv)
If the data ends earlier (e.g. an as-of copy), lists are written for every window date D whose D-1 is in the data.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEV_WINDOW = ("2026-06-04", "2026-09-02")
TEST_WINDOW = ("2026-09-03", "2026-09-30")
K = 20
LOOKBACK = 28


def _codes(col: pd.Series):
    """Integer codes + labels without building millions of strings."""
    if isinstance(col.dtype, pd.CategoricalDtype):
        return col.cat.codes.to_numpy(), np.asarray(col.cat.categories, dtype=str)
    codes, uniq = pd.factorize(col, sort=True)
    return codes, np.asarray(uniq, dtype=str)


def load(data_dir: Path):
    df = pd.read_parquet(data_dir / "daily_sales_inventory.parquet",
                         columns=["date", "store_id", "sku_id", "units_sold", "on_hand_eod"])
    dates = np.sort(df["date"].unique())
    t = np.searchsorted(dates, df["date"].to_numpy())
    st_c, st_u = _codes(df["store_id"])
    sk_c, sk_u = _codes(df["sku_id"])
    pair = st_c.astype(np.int64) * len(sk_u) + sk_c
    codes, uniq = pd.factorize(pair, sort=True)
    T, N = len(dates), len(uniq)
    sales = np.zeros((T, N), dtype=np.float32)
    onhand = np.full((T, N), np.nan, dtype=np.float32)
    sales[t, codes] = df["units_sold"].to_numpy(dtype=np.float32)
    onhand[t, codes] = df["on_hand_eod"].to_numpy(dtype=np.float32, na_value=np.nan)
    del df, t, pair, codes
    # missing on-hand readings: carry the last known value forward
    onhand = pd.DataFrame(onhand).ffill().to_numpy(dtype=np.float32)
    store = st_u[uniq // len(sk_u)]
    sku = sk_u[uniq % len(sk_u)]
    return pd.DatetimeIndex(dates), sales, onhand, store, sku


def features(sales: np.ndarray):
    T, N = sales.shape
    run = np.zeros((T, N), dtype=np.int32)
    r = np.zeros(N, dtype=np.int32)
    for t in range(T):
        r = np.where(sales[t] == 0, r + 1, 0)
        run[t] = r
    cs = np.vstack([np.zeros((1, N), np.float64), np.cumsum(sales, axis=0, dtype=np.float64)])
    rate = np.full((T, N), np.nan, dtype=np.float32)
    cols = np.arange(N)
    for t in range(T):                                        # row by row keeps memory small
        s_idx = np.clip(t - run[t] + 1, 0, T)                 # first day of the current zero run
        lo = np.clip(s_idx - LOOKBACK, 0, None)
        span = s_idx - lo
        rt = (cs[s_idx, cols] - cs[lo, cols]) / np.maximum(span, 1)
        rate[t] = np.where(span >= 7, rt, np.nan)             # need >= 7 days of history before the run
    return run, rate


def make_list(dates, run, rate, onhand, store, sku, window, n_min_run):
    out = []
    stores = np.unique(store)
    for D in pd.date_range(*window, freq="D"):
        t = int(np.searchsorted(dates.values, np.datetime64(D - pd.Timedelta(days=1))))
        if t >= len(dates) or dates[t] != D - pd.Timedelta(days=1):
            continue                                          # D-1 not in the data (e.g. as-of copy)
        t = min(t, len(dates) - 1)
        score = rate[t] * run[t]
        ok = (run[t] >= n_min_run) & (onhand[t] > 0) & np.isfinite(score) & (score > 0)
        for s in stores:
            idx = np.where(ok & (store == s))[0]
            if len(idx) == 0:
                continue
            top = idx[np.argsort(-score[idx], kind="stable")[:K]]
            sc = score[top]
            out.append(pd.DataFrame({
                "date": D.strftime("%Y-%m-%d"), "store_id": s, "sku_id": sku[top],
                "rank": np.arange(1, len(top) + 1),
                "confidence": np.round(1 - np.exp(-sc), 4),
                "reason": [f"No sales for {int(run[t, i])} days while system shows {int(onhand[t, i])} units; "
                           f"it usually sells about {rate[t, i]:.1f} per day" for i in top],
            }))
    cols = ["date", "store_id", "sku_id", "rank", "confidence", "reason"]
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=cols)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--out-dir", default=str(ROOT / "submission"))
    ap.add_argument("--n-min-run", type=int, default=7, help="minimum zero-sales days before flagging (N)")
    a = ap.parse_args()
    t0 = time.time()
    dates, sales, onhand, store, sku = load(Path(a.data))
    print(f"loaded {sales.shape[1]:,} SKU-store series x {sales.shape[0]} days in {time.time() - t0:.1f}s")
    run, rate = features(sales)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, window, fname in [("dev", DEV_WINDOW, "R1_predictions_dev.csv"), ("test", TEST_WINDOW, "R1_predictions.csv")]:
        sub = make_list(dates, run, rate, onhand, store, sku, window, a.n_min_run)
        sub.to_csv(out / fname, index=False)
        print(f"{name:4s}: wrote {len(sub):,} rows -> {out / fname}")
    print(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
