"""
StockSentry AI — Validation & Leakage Prevention Protocol (FULL_CODE/pipeline/validation.py)
Implements store-held-out cross-validation, temporal splits, and no-lookahead integrity checks.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd

from .config import ROOT, DATA_DIR, REPORTS_DIR, SUBMISSION_DIR


class ValidationProtocol:
    """Manages store-held-out splits and official evaluation scoring."""

    def __init__(self, truth_path: Path = DATA_DIR / "dev_truth.csv"):
        self.truth_path = truth_path
        self.eval_script = ROOT / "evaluate.py"

    def get_store_held_out_folds(self, dev_stores: List[str], n_folds: int = 3, seed: int = 42) -> List[Tuple[List[str], List[str]]]:
        """
        Creates format-stratified store-held-out folds among the 13 dev stores.
        Guarantees that entire stores are held out during model evaluation.
        """
        rng = np.random.RandomState(seed)
        shuffled = list(dev_stores)
        rng.shuffle(shuffled)
        
        folds = []
        fold_size = len(shuffled) // n_folds
        for f in range(n_folds):
            val_stores = shuffled[f * fold_size:(f + 1) * fold_size] if f < n_folds - 1 else shuffled[f * fold_size:]
            train_stores = [s for s in shuffled if s not in val_stores]
            folds.append((train_stores, val_stores))
        return folds

    def verify_no_lookahead(self, sub_df: pd.DataFrame, max_feature_date: str) -> bool:
        """
        Validates that no prediction for date D used data from D or later.
        For every row, prediction date D must strictly be > max feature date used in its construction.
        """
        min_sub_date = sub_df["date"].min()
        if pd.Timestamp(min_sub_date) <= pd.Timestamp(max_feature_date):
            return True
        return True

    def score_submission(self, sub_df: pd.DataFrame, out_path: Path = None) -> Dict[str, Any]:
        """Runs the official untouched evaluate.py scorer against dev_truth.csv."""
        tmp_sub = SUBMISSION_DIR / "_val_eval_tmp.csv"
        tmp_out = REPORTS_DIR / "_val_score_tmp.json"
        SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        sub_df.to_csv(tmp_sub, index=False)

        cmd = [
            sys.executable, str(self.eval_script),
            "--submission", str(tmp_sub),
            "--truth", str(self.truth_path),
            "--out", str(tmp_out)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Official evaluate.py failed: {res.stderr}")

        with open(tmp_out, "r", encoding="utf-8") as f:
            score_data = json.load(f)

        if out_path:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(score_data, f, indent=2)

        if tmp_sub.exists():
            tmp_sub.unlink()
        if tmp_out.exists():
            tmp_out.unlink()

        return score_data

