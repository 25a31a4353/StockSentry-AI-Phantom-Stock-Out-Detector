# OFFICIAL DATA AUDIT & SYSTEM ARCHITECTURE AUDIT (PHASE 0)
**Project**: StockSentry AI — The Phantom Stock-Out Detector  
**Challenge**: TalentAP Mega Hackathon 2026 — Problem R1  
**Timestamp**: 2026-10-30T15:20:00+05:30  
**Author**: Principal ML Engineer, Retail Data Scientist & Technical Project Manager  

---

## 1. Git Repository State
- **Active Branch**: `main`
- **Latest Commit**: `8b29630` (`fix(ui): completely remove Master PRD and Demo Video buttons across all pages and add cache-busting`)
- **Remote Origin**: `https://github.com/25a31a4353/StockSentry-AI-Phantom-Stock-Out-Detector.git`
- **Working Tree Cleanliness**: Verified. All temporary and generated files are tracked or git-ignored.

---

## 2. Existing Application Architecture & Entry Points

The repository contains a hybrid full-stack web console, local REST backend, serverless cloud endpoints, and an analytical model pipeline:

```
StockSentry AI Repository
├── Web Client (SPA)
│   ├── index.html                  Entry point for web application
│   ├── styles.css                  CSS stylesheet (Enterprise dark/light theme)
│   ├── data.js                     Client fallback mock dataset & catalog schemas
│   ├── ai-engine.js                Client-side heuristic engine & evaluation viewer
│   └── app.js                      Single-page application UI logic (16 view modules)
├── Backend & API Layer
│   ├── server.py                   Python local HTTP server with SQLite persistence (stocksentry.db)
│   └── api/                        Vercel serverless functions:
│       ├── copilot.js              AI operations copilot assistant
│       ├── evaluate.js             Lightweight evaluation API endpoint
│       ├── ingest.js               POS CSV & ERP ingestion endpoint
│       ├── predict.js              SKU risk scoring endpoint
│       └── verify.js               Handheld physical audit confirmation endpoint
├── Model Pipeline & Scorer
│   ├── baseline/baseline.py        Official organizer benchmark script
│   ├── evaluate.py                 Official organizer evaluation script (untouched authority)
│   ├── official_evaluate.py        Backup copy of official organizer evaluate.py
│   ├── train_model.py              Heuristic ranking pipeline generating submission CSVs
│   └── sample_submission.csv       Official submission format template
└── Data Assets (data/)
    ├── daily_sales_inventory.parquet
    ├── daily_sales_inventory_sample_2stores.csv
    ├── dev_labels.csv
    ├── dev_truth.csv
    ├── store_master.csv
    ├── sku_master.csv
    ├── promotion_calendar.csv
    └── holiday_calendar.csv
```

---

## 3. Inventory of Core Scripts & Artifacts

| File Path | Origin / Authority | Purpose & Status |
|---|---|---|
| `evaluate.py` | Official Organizer | **Scoring Authority**. Evaluates Mean Precision@20 per store-day, Row Recall, Episode Recall, Ceiling, and Delisted Decoy share. |
| `baseline/baseline.py` | Official Organizer | **Benchmark Authority**. Runs zero-sales run heuristic with lookback=28, $N=7$, generating dev and test prediction CSVs. |
| `sample_submission.csv` | Official Organizer | Canonical submission schema template (14,000 rows, 28 dates $\times$ 25 stores $\times$ 20 ranks). |
| `train_model.py` | StockSentry AI | Statistical heuristic pipeline applying Poisson shortfall, slow-mover penalty, and hardcoded delisted filtering. |
| `server.py` | StockSentry AI | Local Python REST service connected to SQLite (`stocksentry.db`). |
| `ai-engine.js` | StockSentry AI | Browser runtime engine used for instant offline demonstrations and diagnostics. |
| `app.js` | StockSentry AI | Web interface managing the Morning Top-20 Verification Queue, SKU deep-dive charts, and Store Network cards. |
| `score.json` | Generated Artifact | Result of running `evaluate.py` on `submission/R1_predictions_dev.csv`. |
| `evaluation_report.json` | Generated Artifact | Summary report consumed by web UI. |

---

## 4. Origin Classification: Official Organizer vs. StockSentry Code

### A. Official Organizer Files (Strictly Preserved & Untouched)
1. `evaluate.py` (SHA-256 verified against organizer zip).
2. `baseline/baseline.py` (Untouched baseline script).
3. `sample_submission.csv` (Canonical format reference).
4. `data/daily_sales_inventory.parquet` (Complete 7,970,112-row time-series panel).
5. `data/daily_sales_inventory_sample_2stores.csv` (Excel sample for 2 stores).
6. `data/dev_labels.csv` (2,905 labeled episodes with start/end dates).
7. `data/dev_truth.csv` (24,639 daily ground-truth labeled rows across 13 dev stores, identical to `dev_truth.csv.gz`).
8. `data/store_master.csv` (Metadata for 25 stores: format, tier, label group).
9. `data/sku_master.csv` (Metadata for 800 SKUs: category, brand, cost, margin, pack).
10. `data/promotion_calendar.csv` (1,789 promotional campaigns).
11. `data/holiday_calendar.csv` (27 national/regional holidays).

### B. StockSentry Code
1. `FULL_CODE/pipeline/*` (Data loader, feature engineering, statistical models, ML ranker, evaluator).
2. `train_model.py` (Legacy prototype script).
3. `server.py` & `api/*` (REST APIs).
4. `index.html`, `app.js`, `styles.css`, `data.js`, `ai-engine.js` (Web dashboard).

---

## 5. Audit: Does the Existing Training Script Actually Use Public Labels?

**Finding**: **NO.**
- `train_model.py` loads `daily_sales_inventory.parquet`, computes moving-window sales velocity and zero streak length, and ranks SKUs using a fixed heuristic formula.
- Neither `data/dev_labels.csv` nor `data/dev_truth.csv` is used during feature calculation or parameter fitting.
- `dev_truth.csv` is only invoked in the final step via `subprocess.run(["python", "evaluate.py", ...])` to score the generated predictions.
- **Defect Identified**: The model does not optimize any objective function against the training labels; it is an unsupervised heuristic.

---

## 6. Audit: Is the Existing Model Genuinely Trained, Hand-Engineered, or Hybrid?

**Finding**: **Hand-Engineered Heuristic with Hardcoded Decoy Lists.**
- The score is formulated as:
  $$\text{score} = (1 - e^{-\text{expected\_volume}}) \times \text{expected\_volume}^{0.85} \times \text{promo\_mult} \times \text{slow\_penalty}$$
- The exponent $0.85$, the promo multiplier $1.30$, the slow-mover cutoff $0.25$, and the penalty $0.45$ were chosen by manual tuning.
- **Critical Vulnerability**: Lines 104–109 explicitly hardcode four SKU IDs:
  ```python
  known_delisted = {'SKU-0AE5LI', 'SKU-BLVFYH', 'SKU-D8ZP2B', 'SKU-SFOGXE'}
  for s_id in known_delisted:
      if s_id in sku_indices:
          delisted_mask[:, sku_indices[s_id]] = True
  ```
  Hardcoding specific SKU IDs from the development set violates competition integrity and will fail completely on the 12 unseen test stores if different SKUs are phased out. A point-in-time, generalizable chain-wide delisting rule must replace this hardcoded set.

---

## 7. Audit: Can the Reported 40.04% Precision@20 Be Reproduced Exactly?

**Finding**: **YES, Exactly Verified.**
- Executed command:
  ```bash
  python evaluate.py --submission submission/R1_predictions_dev.csv --truth data/dev_truth.csv --out score_check.json
  ```
- **Exact Output**:
  ```text
  Scored store-days          : 1183 (91 dates x 13 stores)
  PRIMARY  precision@20       : 0.4004   (0..1, higher is better)
    best possible (ceiling)  : 0.8656
  Row recall                 : 0.4091  (9473 of 23156 positive rows)
  Episode recall             : 0.2127  (of 2868 positive episodes)
  Flags spent on delisted    : 0.0000
  Stretch type accuracy      : 0.7810  (n=9473)
  ```
- The result is 100% reproducible with the existing CSV file, but its $0.00\%$ delisted decoy flag rate is artificially achieved by the hardcoded SKU list.

---

## 8. Audit: Does the Existing Prediction Generator Follow the No-Look-Ahead Rule?

**Finding**: **PARTIALLY COMPLIANT with ONE CRITICAL FLAW.**
- **Compliant Aspect**: For any prediction date $D$, the feature indexing uses:
  ```python
  t = int(np.searchsorted(dates.values, np.datetime64(D - pd.Timedelta(days=1))))
  ```
  This strictly limits sales, streaks, and on-hand inventory to day $D-1$ (what the store manager knows at opening on day $D$).
- **Non-Compliant Flaw**: The hardcoded `known_delisted` mask marks those SKUs as delisted across the entire calendar, including dates *before* their sales stopped and without inferring delisting dynamically as of $D-1$.
- **Remediation**: In Phase 7, we implement a point-in-time detector that flags an item as delisted at day $D-1$ only if $\ge 8$ stores simultaneously record persistent zero sales with frozen positive stock over the preceding 14 days.

---

## Conclusion & Action Plan
Phase 0 audit is complete and fully verified. We proceed immediately to:
1. **Phase 1 & 2**: Catalog and validate all 8 data files using a reusable ingestion module.
2. **Phase 3**: Run the official untouched organizer baseline (`baseline/baseline.py`) and record its genuine score.
3. **Phase 4**: Establish a store-held-out cross-validation split (e.g. 9 train stores / 4 validation stores).
4. **Phase 5 & 6**: Develop and compare Poisson statistical modeling, feature-engineered supervised ranking (LightGBM/GBDT), and an ensemble.
5. **Phase 7**: Implement a legitimate point-in-time delisting detector without SKU hardcoding.
6. **Phase 8–13**: Build the unified pipeline under `FULL_CODE/` and generate the final validated submission package.

