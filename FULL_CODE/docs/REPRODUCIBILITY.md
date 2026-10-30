# StockSentry AI — Reproducibility & Execution Guide
**Project**: StockSentry AI — The Phantom Stock-Out Detector  
**Challenge**: TalentAP Mega Hackathon 2026 — Problem R1  

---

## 1. Environment & Prerequisites

- **Python Version**: Python 3.9+ (Tested on Python 3.14 on Windows 11)
- **Core Dependencies**:
  ```bash
  pip install -r FULL_CODE/requirements.txt
  ```
  *(Requires only `numpy`, `pandas`, `pyarrow`, `scipy`, and `pytest`. Zero external GPU or paid cloud API dependencies required for core prediction and evaluation.)*

---

## 2. Directory Structure Verification

Ensure the root repository structure matches the official competition layout:

```text
StockSentry/
├── README.md                           Organizer R1 Challenge Guide
├── evaluate.py                         Official Scorer (untouched authority)
├── sample_submission.csv               Official format template (14,000 rows)
├── baseline/
│   └── baseline.py                     Official Organizer Baseline Script
├── data/
│   ├── daily_sales_inventory.parquet   Full 7.97M row panel (local, not in git)
│   ├── daily_sales_inventory_sample_2stores.csv
│   ├── dev_labels.csv                  2,905 labeled episodes
│   ├── dev_truth.csv                   24,639 daily ground truth rows
│   ├── store_master.csv                25 stores metadata
│   ├── sku_master.csv                  800 SKUs metadata
│   ├── promotion_calendar.csv          1,789 promotion records
│   └── holiday_calendar.csv            27 holiday records
├── submission/
│   ├── R1_predictions.csv              Final Official Test Submission (14,000 rows)
│   └── R1_predictions_dev.csv          Dev Evaluation Predictions (45,500 rows)
└── FULL_CODE/
    ├── pipeline/                       Clean modular pipeline
    │   ├── config.py
    │   ├── data_loader.py
    │   ├── features.py
    │   ├── predict.py
    │   ├── validation.py
    │   ├── submission_validator.py
    │   ├── impact.py
    │   └── main.py                     Single Master Entry Point
    ├── reports/                        Generated machine-readable artifacts
    │   ├── baseline_score.json
    │   ├── final_dev_score.json
    │   ├── experiment_results.csv
    │   ├── data_quality_report.json
    │   └── submission_validation.json
    ├── docs/
    │   ├── OFFICIAL_DATA_AUDIT.md
    │   ├── MODEL_CARD.md
    │   └── REPRODUCIBILITY.md
    └── tests/
        └── test_pipeline.py
```

---

## 3. Step-by-Step Reproduction Instructions

### Step 1: Run the Official Organizer Baseline
Execute the organizer's baseline model to generate baseline predictions and score them:
```bash
python baseline/baseline.py --out-dir submission_baseline
python evaluate.py --submission submission_baseline/R1_predictions_dev.csv --truth data/dev_truth.csv --out FULL_CODE/reports/baseline_score.json
```
**Expected Output**:
- Primary Precision@20: `0.3965` (39.65%)
- Flags Spent on Delisted Decoys: `0.0520` (5.20%)
- Row Recall: `0.4051` (40.51%)

---

### Step 2: Run the Model Comparison & Parameter Sweeps
Execute the systematic experiment runner:
```bash
python FULL_CODE/pipeline/run_experiments.py
```
This evaluates Model A (Baseline), Model B (Delisted Filter), Model C (Poisson Bayesian), Model D (Poisson + Promo), and Model E (Hybrid), and writes `FULL_CODE/reports/experiment_results.csv`.

---

### Step 3: Run the StockSentry AI Master Pipeline
Execute the canonical end-to-end pipeline:
```bash
python FULL_CODE/pipeline/main.py
```
This single command:
1. Ingests and validates the 7.97M row dataset (`data_quality_report.json`).
2. Builds point-in-time rates, zero streaks, and dynamic delisting masks.
3. Generates dev predictions (`submission/R1_predictions_dev.csv`).
4. Scores dev predictions with untouched `evaluate.py` (`final_dev_score.json`).
5. Generates final official test predictions (`submission/R1_predictions.csv`).
6. Runs format validation against `sample_submission.csv` (`submission_validation.json`).
7. Calculates rupee recovery arithmetic.

**Expected Final Benchmark**:
```text
Primary Precision@20       : 0.4054 (40.54% vs Baseline 39.65%)
Share of Theoretical Ceiling: 46.83% (vs Baseline 45.81%)
Total True Hits Captured   : 9,591 hits (+210 over baseline)
Flags Spent on Delisted    : 0.0226 (2.26% vs Baseline 5.20%)
Stretch Type Accuracy      : 76.11%
Submission Validation      : PASSED
```

---

### Step 4: Run Unit Tests
Execute the automated test suite:
```bash
python -m pytest FULL_CODE/tests/test_pipeline.py -v
```
**Expected Output**:
- 5 tests collected, 5 passed.

---

### Step 5: Verify the Submission Contract
Verify the generated test submission file:
```bash
python -c "from FULL_CODE.pipeline.submission_validator import validate_submission_file; r = validate_submission_file(); print('Valid:', r['is_valid'], 'Rows:', r['row_count'], 'Dates:', r['n_unique_dates'], 'Stores:', r['n_unique_stores'])"
```
**Expected Output**:
```text
Valid: True Rows: 14000 Dates: 28 Stores: 25
```

