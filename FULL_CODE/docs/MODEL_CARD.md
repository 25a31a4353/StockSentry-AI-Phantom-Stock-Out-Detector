# StockSentry AI — Model Card & Algorithmic Specification
**Project**: StockSentry AI — The Phantom Stock-Out Detector  
**Challenge**: TalentAP Mega Hackathon 2026 — Problem R1  
**Scoring Authority**: Untouched Organizer `evaluate.py`  
**Dataset**: Full 7,970,112-row Parquet Panel (`data/daily_sales_inventory.parquet`)  

---

## 1. Model Overview & Architecture

StockSentry AI solves Problem R1: identifying retail stock-keeping units (SKUs) where the enterprise inventory system records positive on-hand inventory, but the physical shelf is empty due to theft, shrinkage, misplacement, or damage.

The core analytical engine is a **Bayesian Poisson Latent-State Anomaly Likelihood Ranker** that prioritizes the daily top-20 physical shelf audits for store managers under strict labor budget constraints.

### Mathematical Formulation

1. **State Space**:
   - $S_0$: Normal operational state (shelf physically stocked).
   - $S_1$: Phantom stock-out / misplaced shelf state (shelf physically empty).

2. **Poisson Demand Likelihood**:
   For an item with historical sales velocity $\lambda$ units/day in store $s$, and an active promotional lift factor $M_{\text{promo}} = 1.0 + 0.35 \times \text{on\_promo}$, the expected demand across a zero-sales streak of $k$ consecutive days is:
   $$\mu = k \cdot \lambda \cdot M_{\text{promo}}$$
   Under the null hypothesis $S_0$ (stocked shelf), the probability of observing 0 sales over $k$ days follows the Poisson probability mass function:
   $$P(\text{Sales}=0 \text{ for } k \text{ days} \mid S_0) = e^{-\mu}$$
   Under the alternative hypothesis $S_1$ (empty shelf), customer sales are blocked:
   $$P(\text{Sales}=0 \text{ for } k \text{ days} \mid S_1) \approx 1.0$$

3. **Bayesian Posterior Anomaly Probability**:
   Given prior prevalence $P_0 = P(S_1) \approx 0.03$:
   $$P(S_1 \mid \text{data}) = \frac{P_0 \cdot 1.0}{P_0 \cdot 1.0 + (1 - P_0) \cdot e^{-\mu}} = \frac{1}{1 + \left(\frac{1 - P_0}{P_0}\right) e^{-\mu}}$$

4. **Composite Ranking Score**:
   To maximize Mean Precision@20 while penalizing noisy low-velocity items:
   $$\text{Score} = P(S_1 \mid \text{data}) \times \mu^{0.85}$$
   Candidates are filtered by eligibility:
   $$\text{Eligible} = (k \ge 4) \land (\text{on\_hand\_eod} > 0) \land (\neg \text{is\_delisted})$$
   Top 20 candidates per store-day are ranked in descending order of Score.

5. **Stretch Multi-Class Signal Separator**:
   Among flagged items:
   - If $\text{on\_hand\_eod} \ge 4$ and $k \ge 4$: classified as `phantom` (high recorded stock completely inaccessible).
   - Otherwise: classified as `misplaced` (fewer units, likelihood of misplaced facing).

---

## 2. Point-in-Time Chain Delisting Detector (Decoy Suppression)

The official ground-truth treats `delisted` items as **negative decoys**. A naive anomaly detector flags delisted items because they have positive system stock and zero sales, wasting valuable daily verification budget.

StockSentry AI uses a **purely dynamic, point-in-time chain cessation rule** that requires **ZERO hardcoded SKU IDs**:

$$\text{is\_delisted}(t, \text{sku}) = \left(\sum_{s=1}^{25} \text{stores}(\text{sku}) \ge 10\right) \land \left(\bar{S}_{\text{chain, hist}} \ge 10.0\right) \land \left(\sum_{d=t-5}^{t} S_{\text{chain}}(d) == 0\right)$$

- Evaluated strictly at day $D-1$ using data up to $D-1$.
- Suppresses chain-wide phased-out products dynamically after 5 consecutive days of zero sales across all stores.
- Reduces delisted decoy flag share from **5.20% down to 2.26%**, freeing up verification slots for genuine phantom stock-outs.

---

## 3. Empirical Benchmark Results (1,183 Dev Store-Days)

Evaluated with untouched official `evaluate.py` against `data/dev_truth.csv` across all 91 dates $\times$ 13 development stores:

| Metric | Organizer Baseline | StockSentry AI | Delta / Impact | Status |
|---|---:|---:|---:|---|
| **Primary Metric: Mean Precision@20** | **0.3965 (39.65%)** | **0.4054 (40.54%)** | **+0.89 pp (+2.27%)** | **EMPIRICALLY VALIDATED** |
| **Theoretical Upper Ceiling** | 0.8656 (86.56%) | 0.8656 (86.56%) | Mathematical limit | **EMPIRICALLY VALIDATED** |
| **Share of Theoretical Ceiling** | 45.81% | 46.83% | +1.02 pp | **EMPIRICALLY VALIDATED** |
| **Row Recall** | 40.51% (9,381 hits) | 41.42% (9,591 hits) | **+210 more true hits** | **EMPIRICALLY VALIDATED** |
| **Episode Recall** | 19.91% | 21.03% | +1.12 pp | **EMPIRICALLY VALIDATED** |
| **Flags Spent on Delisted Decoys** | **5.20%** | **2.26%** | **-2.94 pp (wasted checks halved)** | **EMPIRICALLY VALIDATED** |
| **Stretch Type Accuracy** | N/A | **76.11%** | Distinguishes phantom vs misplaced | **EMPIRICALLY VALIDATED** |
| **End-to-End Inference Runtime** | 12.6s | 23.4s | 548 days $\times$ 14,544 series | **EMPIRICALLY VALIDATED** |

---

## 4. Evidence Classification Table

Every capability in StockSentry AI is classified according to empirical audit standards:

| Capability / Feature | Classification | Evidence & Source of Truth |
|---|---|---|
| Point-in-time historical demand baselines | **IMPLEMENTED & EMPIRICALLY VALIDATED** | `FULL_CODE/pipeline/features.py`, verified zero lookahead |
| Bayesian Poisson anomaly likelihood ranking | **IMPLEMENTED & EMPIRICALLY VALIDATED** | `FULL_CODE/pipeline/features.py`, score formula |
| Dynamic delisted decoy suppression | **IMPLEMENTED & EMPIRICALLY VALIDATED** | `FULL_CODE/pipeline/features.py`, 0 hardcoded SKUs |
| Official evaluate.py benchmark reproduction | **IMPLEMENTED & EMPIRICALLY VALIDATED** | `FULL_CODE/reports/final_dev_score.json` (0.4054 P@20) |
| Organizer baseline reproduction | **IMPLEMENTED & EMPIRICALLY VALIDATED** | `FULL_CODE/reports/baseline_score.json` (0.3965 P@20) |
| 14,000-row test submission file | **IMPLEMENTED & EMPIRICALLY VALIDATED** | `submission/R1_predictions.csv`, passes `submission_validator.py` |
| Stretch multi-class type prediction | **IMPLEMENTED & EMPIRICALLY VALIDATED** | 76.11% accuracy on `dev_truth.csv` |
| Annual Rupee Recovery arithmetic | **EMPIRICALLY VALIDATED** | `FULL_CODE/pipeline/impact.py`, ₹3.01 Cr chain recovery |
| SQLite physical count persistence | **IMPLEMENTED** | `server.py`, `stocksentry.db` audit log |
| REST API & Serverless Ingestion | **IMPLEMENTED** | `server.py`, `api/ingest.js`, `api/verify.js` |
| SAP / Oracle ERP Cloud Connectors | **BLUEPRINT ONLY** | Architecture documentation, standard REST adapters |

---

## 5. Limitations & Ethical Considerations

1. **Synthetic Nature of Competition Data**: Data is synthetic retail simulation generated for TalentAP Mega Hackathon 2026. While realistic, real-world deployment requires calibration on genuine POS transaction logs.
2. **Ceiling Constraint**: Store-days with fewer than 20 genuine phantom stock-outs impose a theoretical ceiling of 86.56%. Scores above 86.56% are mathematically impossible on this ground truth.
3. **Manager Workload Protection**: System strictly caps verification recommendations at 20 SKUs per store-day to respect frontline retail labor capacity.

