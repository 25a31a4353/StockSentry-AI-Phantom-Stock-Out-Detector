# STOCKSENTRY AI — FINAL ROUND 1 RELEASE & EVIDENCE-LOCK REPORT
**Project**: StockSentry AI — The Phantom Stock-Out Detector  
**Competition**: TalentAP Mega Hackathon 2026 — Problem R1  
**Scoring Authority**: Untouched Organizer `evaluate.py`  
**Evaluation Scope**: 1,183 Development Store-Days (91 Dates $\times$ 13 Dev Stores)  
**Submission Artifact**: `submission/R1_predictions.csv` (14,000 Rows, 25 Stores $\times$ 28 Dates)  
**Timestamp**: 2026-10-30T15:58:00+05:30  
**Release State**: FINAL LOCK  

---

## 1. Executive Summary

StockSentry AI Round 1 is complete, verified, and locked. Using the official full dataset (7.97M rows across 25 stores and 800 SKUs), we established the untouched organizer baseline locally, conducted a leakage audit with zero lookahead, and improved the primary competition metric (**Mean Precision@20 per Store-Day**) from **39.65%** to **40.55%** (+0.90 percentage points, capturing +213 additional verified phantom/misplaced shelf-outs across 1,183 development store-days).

All 14,000 test predictions have been generated, strictly validated against the official schema, and locked into `submission/R1_predictions.csv`.

---

## 2. Official Dataset Details

- **Time-Series Panel (`data/daily_sales_inventory.parquet`)**:
  - Total records: **7,970,112 rows**
  - Date span: **548 days** (2025-04-01 through 2026-09-30)
  - Stores: **25 stores** (13 development labeled, 12 hidden test)
  - SKUs: **800 SKUs**
  - Unique store-SKU time series: **14,544 active series** (reflecting realistic retail assortment sizes across Hyper, Market, and Express formats)
  - Missing inventory records: **4,987 rows** (0.06%), safely forward-filled; zero-sales with missing on-hand are strictly unflagged.
  - Missing sales records: **0**
  - Active promotion days: **1,034,623 store-SKU-days** (~13%)
- **Ground Truth (`data/dev_truth.csv` & `data/dev_labels.csv`)**:
  - 24,639 labeled store-SKU-day rows across 91 dates (2026-06-04 to 2026-09-02) and 13 dev stores.
  - Positive labels: **17,618 phantom** (71.5%) + **5,538 misplaced** (22.5%) = **23,156 positive shelf-outs**.
  - Negative decoy: **1,483 delisted** (6.0%).

---

## 3. Benchmark Score Comparison

Scored using untouched official `evaluate.py` against `data/dev_truth.csv`:

| Evaluation Metric | Official Baseline | Previous StockSentry | Final StockSentry Lock | Absolute Gain | Relative Gain |
|---|---:|---:|---:|---:|---:|
| **Primary: Mean Precision@20** | **0.3965 (39.65%)** | **0.4004 (40.04%)** | **0.4055 (40.55%)** | **+0.8996 pp** | **+2.27%** |
| **Theoretical Upper Ceiling** | 0.8656 (86.56%) | 0.8656 (86.56%) | 0.8656 (86.56%) | 0.00 pp | — |
| **Share of Theoretical Ceiling** | 45.81% | 46.25% | **46.85%** | **+1.04 pp** | **+2.27%** |
| **Row Recall** | 0.4051 (40.51%) | 0.4091 (40.91%) | **0.4143 (41.43%)** | **+0.92 pp** | **+2.27%** |
| **Episode Recall** | 0.1991 (19.91%) | 0.2127 (21.27%) | **0.2096 (20.96%)** | **+1.05 pp** | **+5.27%** |
| **Total Verified Hits (Dev)** | 9,381 hits | 9,473 hits | **9,594 hits** | **+213 hits** | **+2.27%** |
| **Flags on Delisted Decoys** | **5.20% (1,231 waste)** | **0.00% (hardcoded)** | **2.26% (dynamic)** | **-2.94 pp** | **-56.5%** |
| **Stretch Type Accuracy** | N/A | 78.10% | **76.15%** | Validated | — |

---

## 4. Final Model Name & Exact Ranking Logic

### Technically Accurate Model Name
**"Point-in-Time Bayesian Poisson Demand–Inventory Anomaly Ranker"**

### Mathematical Ranking Logic
For any store $s$ and SKU $i$ evaluated for morning audit list on date $D$:
1. **Feature Indexing**: Strictly accesses historical data up to $t = D - 1$.
2. **Baseline Demand Rate ($\lambda$)**:
   $$\lambda = \frac{1}{\text{lookback}} \sum_{d=t-k-\text{lookback}+1}^{t-k} \text{units\_sold}(d)$$
   Calculated over the 28-day window strictly *before* the zero-sales streak began.
3. **Expected Missed Volume ($\mu$) with Promotional Lift**:
   $$\mu = k \cdot \lambda \cdot (1.0 + 0.20 \times \text{on\_promo}(t))$$
4. **Bayesian Posterior Anomaly Probability**:
   $$P(S_1 \mid \text{data}) = \frac{1}{1 + \left(\frac{1 - P_0}{P_0}\right) e^{-\mu}},\quad \text{where } P_0 = 0.03$$
5. **Priority Ranking Score**:
   $$\text{Score} = P(S_1 \mid \text{data}) \times \mu^{0.85}$$
6. **Candidate Eligibility**:
   $$\text{Eligible} = (k \ge 4) \land (\text{on\_hand\_eod}(t) > 0) \land \text{isfinite}(\text{Score}) \land (\text{Score} > 0) \land (\neg \text{is\_delisted}(t))$$
   The top $\min(20, |\text{Eligible}|)$ candidates are ranked in descending order of Score.

---

## 5. Delisted / False-Positive Decoy Control (Zero Hardcoding)

In retail, delisted products stop selling chain-wide because head office phased them out, yet frozen system on-hand remains in the ERP. Naive models waste 5.20% of their checks on these decoys.

### Dynamic Point-in-Time Cessation Rule
$$\text{is\_delisted}(t, \text{sku}) = \left(N_{\text{stores}}(\text{sku}) \ge 10\right) \land \left(\bar{S}_{\text{hist}} \ge 10.0\right) \land \left(\sum_{d=t-4}^t S_{\text{chain}}(d) == 0\right)$$
- Evaluated strictly at day $D-1$ across whatever stores exist in the chain up to that date.
- Zero hardcoded SKU names.
- Cuts decoy waste from **5.20% down to 2.26%**, freeing up verification slots for genuine shelf stock-outs.

---

## 6. Leakage & Point-in-Time Audit

A dedicated automated test suite ([`FULL_CODE/tests/test_leakage_audit.py`](file:///c:/Users/SHANMUKHESWAR/OneDrive/Desktop/Phantom_stock/StockSentry-AI-Phantom-Stock-Out-Detector/FULL_CODE/tests/test_leakage_audit.py)) was executed:
- **Truncation Equivalence Tests**: For dates `2026-07-31`, `2026-08-15`, `2026-08-31`, and `2026-09-02`, the full dataset was truncated so no rows after $D-1$ existed. The predictions generated on the truncated dataset matched the full dataset 100% bit-for-bit (ranks, confidences, reasons, types).
- **Label Insulation**: Verified that `dev_truth.csv` and `dev_labels.csv` are not imported or referenced by `features.py` or `predict.py`.
- **Audit Verdict**: **PASS (Zero Lookahead Leakage)**.

---

## 7. Stretch Goal: Multi-Class Signal Separation

Evaluated directly against `label_type` in `dev_truth.csv`:
- Rule-based operational heuristic:
  - If $\text{on\_hand\_eod} \ge 4$ units and $k \ge 4$ days: classified as `phantom` (substantial recorded stock unreachable by shoppers).
  - Otherwise: classified as `misplaced` (low remaining stock, likely misplaced in wrong aisle/facing).
- Delisted SKUs are filtered out of the queue.
- **Accuracy**: **76.15%** (7,306 correct out of 9,594 flagged hits).
- Note: This is an empirical rule-based separator, not a trained neural or tree classifier.

---

## 8. Missing Inventory & Monthly Reset Handling

1. **4,987 Missing `on_hand_eod` Rows**:
   - Safely forward-filled from last known system reading.
   - Any series with uninitialized (leading) NaNs evaluates to `False` under `on_hand > 0` and is never flagged.
2. **Monthly Stock Resets**:
   - Stores execute cycle counts on day 1 of each calendar month. The minimum streak $N=4$ naturally cushions against single-day reset dips, allowing the model to rebound quickly by mid-month.

---

## 9. Final Official Submission Validation

- **Target File**: [`submission/R1_predictions.csv`](file:///c:/Users/SHANMUKHESWAR/OneDrive/Desktop/Phantom_stock/StockSentry-AI-Phantom-Stock-Out-Detector/submission/R1_predictions.csv)
- **Validation Artifact**: [`FULL_CODE/reports/submission_validation.json`](file:///c:/Users/SHANMUKHESWAR/OneDrive/Desktop/Phantom_stock/StockSentry-AI-Phantom-Stock-Out-Detector/FULL_CODE/reports/submission_validation.json)
- **Validation Results**:
  - Total rows: **14,000** (exactly 25 stores $\times$ 28 test dates $\times$ 20 ranks).
  - Date range: `2026-09-03` to `2026-09-30`.
  - Stores: All 25 stores represented (`STR-06EU` through `STR-YMG4`).
  - Max rows per store-day: **20**.
  - Rank integrity: Integers $1 \dots 20$, strictly unique per store-day.
  - Duplicate keys: **0**.
  - Confidence range: $[0.5941, 0.9900]$, no NaNs.
  - Reasons: 100% non-blank plain-English explanations.
  - **Verdict**: **PASSED (100% Contract Compliant)**.

---

## 10. How to Reproduce Everything

From the repository root:
```bash
# 1. Run all unit tests & leakage audits (10 tests)
python -m pytest FULL_CODE/tests -p no:qt -v

# 2. Run untouched organizer baseline
python baseline/baseline.py --out-dir submission_baseline
python evaluate.py --submission submission_baseline/R1_predictions_dev.csv --truth data/dev_truth.csv --out FULL_CODE/reports/baseline_score.json

# 3. Run StockSentry AI Master Pipeline (generates dev & test predictions, scores with evaluate.py, validates format)
python FULL_CODE/pipeline/main.py
```

---

## 11. Strict Compliance & Negative Claims (What Must NOT Be Claimed)

1. **Public Development Score Only**: The **40.55% Precision@20** is measured strictly on the public development stores and dates (13 stores, 91 dates). Hidden test performance on the 12 unseen stores cannot be known until hackathon organizers run their scoring.
2. **No Guaranteed Revenue**: The ₹3.01 Crore annual recovery estimate is an illustrative scenario derived from catalog averages (₹185 price, 2.2 units/day demand, 12 prevented lost days); it is not guaranteed real-world cash.
3. **No Trained Neural/Tree AI**: The model is a **point-in-time Bayesian Poisson anomaly ranker**, not a trained deep neural network or XGBoost model.
4. **No Live ERP Integration**: Live SAP S/4HANA or Oracle Retail integrations are architectural blueprints; the working system uses standard JSON REST APIs and local SQLite persistence.
