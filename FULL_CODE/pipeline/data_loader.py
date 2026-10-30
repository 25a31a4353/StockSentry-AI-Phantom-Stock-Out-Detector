"""
StockSentry AI — Reusable Data Ingestion Module (FULL_CODE/pipeline/data_loader.py)
Loads and validates full official competition panel and reference tables.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Tuple, Dict, Any

import numpy as np
import pandas as pd

from .config import DATA_DIR


def _codes(col: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
    """Memory-efficient integer factorizer avoiding string allocations."""
    if isinstance(col.dtype, pd.CategoricalDtype):
        return col.cat.codes.to_numpy(), np.asarray(col.cat.categories, dtype=str)
    codes, uniq = pd.factorize(col, sort=True)
    return codes, np.asarray(uniq, dtype=str)


def load_master_tables(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    """Loads all store and SKU metadata and promotion/holiday calendars."""
    tables = {
        "store_master": pd.read_csv(data_dir / "store_master.csv"),
        "sku_master": pd.read_csv(data_dir / "sku_master.csv"),
        "promotion_calendar": pd.read_csv(data_dir / "promotion_calendar.csv"),
        "holiday_calendar": pd.read_csv(data_dir / "holiday_calendar.csv"),
    }
    if (data_dir / "dev_truth.csv").exists():
        tables["dev_truth"] = pd.read_csv(data_dir / "dev_truth.csv")
    if (data_dir / "dev_labels.csv").exists():
        tables["dev_labels"] = pd.read_csv(data_dir / "dev_labels.csv")
    return tables


def load_timeseries_panel(data_dir: Path = DATA_DIR) -> Tuple[pd.DatetimeIndex, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Ingests official 7,970,112-row parquet dataset into optimized 2D numpy matrices:
    Returns: (dates, sales[T, N], onhand[T, N], promo[T, N], store[N], sku[N])
    """
    parquet_path = data_dir / "daily_sales_inventory.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Required official dataset not found: {parquet_path}")

    t0 = time.time()
    df = pd.read_parquet(
        parquet_path,
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
    # Missing on-hand readings forward fill
    onhand = pd.DataFrame(onhand).ffill().to_numpy(dtype=np.float32)
    store = st_u[uniq // len(sk_u)]
    sku = sk_u[uniq % len(sk_u)]

    print(f"[+] Loaded {N:,} series x {T} days from parquet in {time.time() - t0:.1f}s")
    return pd.DatetimeIndex(dates), sales, onhand, promo, store, sku

