"""
StockSentry AI — Official Submission Format Validator (FULL_CODE/pipeline/submission_validator.py)
Validates submission CSV strictly against official Hackathon contract and sample_submission.csv.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from .config import ROOT, SUBMISSION_DIR, REPORTS_DIR, TEST_WINDOW, MAX_PER_STORE_DAY


def validate_submission_file(sub_path: Path = SUBMISSION_DIR / "R1_predictions.csv", sample_path: Path = ROOT / "sample_submission.csv") -> Dict[str, Any]:
    """Validates row counts, columns, rank constraints, dates, and schema."""
    if not sub_path.exists():
        raise FileNotFoundError(f"Submission file does not exist: {sub_path}")

    sub = pd.read_csv(sub_path)
    sample = pd.read_csv(sample_path) if sample_path.exists() else None

    report = {
        "file_name": sub_path.name,
        "row_count": len(sub),
        "columns": sub.columns.tolist(),
        "is_valid": True,
        "errors": [],
        "warnings": []
    }

    # 1. Required columns
    required_cols = ["date", "store_id", "sku_id", "rank", "confidence", "reason"]
    for col in required_cols:
        if col not in sub.columns:
            report["errors"].append(f"Missing required column: {col}")
            report["is_valid"] = False

    # 2. Date format and range
    try:
        sub_dates = pd.to_datetime(sub["date"], format="%Y-%m-%d")
        min_date, max_date = sub["date"].min(), sub["date"].max()
        report["date_range"] = [min_date, max_date]
        report["n_unique_dates"] = sub["date"].nunique()
        if min_date < TEST_WINDOW[0] or max_date > TEST_WINDOW[1]:
            report["warnings"].append(f"Dates outside test window {TEST_WINDOW}: {min_date} to {max_date}")
    except Exception as e:
        report["errors"].append(f"Invalid date format (must be YYYY-MM-DD): {e}")
        report["is_valid"] = False

    # 3. Store count
    n_stores = sub["store_id"].nunique()
    report["n_unique_stores"] = n_stores
    if n_stores < 25:
        report["warnings"].append(f"Submission covers {n_stores}/25 stores")

    # 4. Rank integrity
    grouped = sub.groupby(["date", "store_id"])
    report["n_store_days"] = len(grouped)
    max_rows_per_sd = grouped.size().max()
    report["max_rows_per_store_day"] = int(max_rows_per_sd)
    if max_rows_per_sd > MAX_PER_STORE_DAY:
        report["errors"].append(f"Exceeded max rows per store-day ({max_rows_per_sd} > {MAX_PER_STORE_DAY})")
        report["is_valid"] = False

    # Check rank values
    rank_min = sub["rank"].min()
    rank_max = sub["rank"].max()
    report["rank_range"] = [int(rank_min), int(rank_max)]
    if rank_min < 1 or rank_max > MAX_PER_STORE_DAY:
        report["errors"].append(f"Rank outside 1..{MAX_PER_STORE_DAY}: [{rank_min}, {rank_max}]")
        report["is_valid"] = False

    # Check rank uniqueness per store-day
    rank_dup = sub.duplicated(subset=["date", "store_id", "rank"]).sum()
    if rank_dup > 0:
        report["errors"].append(f"Duplicate ranks detected: {rank_dup} collisions")
        report["is_valid"] = False

    # 5. SKU uniqueness per store-day
    sku_dup = sub.duplicated(subset=["date", "store_id", "sku_id"]).sum()
    if sku_dup > 0:
        report["errors"].append(f"Duplicate (date, store, SKU) records: {sku_dup}")
        report["is_valid"] = False

    # 6. Confidence bounds
    conf_min = sub["confidence"].min()
    conf_max = sub["confidence"].max()
    report["confidence_range"] = [float(conf_min), float(conf_max)]
    if conf_min < 0.0 or conf_max > 1.0 or sub["confidence"].isna().any():
        report["errors"].append(f"Confidence values out of bounds [0, 1] or NaN: [{conf_min}, {conf_max}]")
        report["is_valid"] = False

    # 7. Blank reasons
    blank_reasons = (sub["reason"].isna() | (sub["reason"].str.strip() == "")).sum()
    report["blank_reasons_count"] = int(blank_reasons)
    if blank_reasons > 0:
        report["errors"].append(f"Blank reasons detected: {blank_reasons} rows")
        report["is_valid"] = False

    # 8. Stretch predicted_type check
    if "predicted_type" in sub.columns:
        report["has_predicted_type"] = True
        report["predicted_type_distribution"] = sub["predicted_type"].value_counts().to_dict()

    # Save report
    out_json = REPORTS_DIR / "submission_validation.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report

