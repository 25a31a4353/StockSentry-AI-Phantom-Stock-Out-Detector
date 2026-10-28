# StockSentry AI — Phantom Stock-Out Detector & Retail Operations Console

> **AI-powered retail inventory intelligence for detecting suspicious SKU–store stock mismatches, prioritizing the daily Top-20 physical verification checks, and recovering invisible lost sales.**

---

## 📌 Problem Overview (The R1 Challenge)

In retail supply chains, an ERP system can report that a product has units on hand (e.g. 6 units), while on the physical shelf, the item has been **lost, stolen (shrinkage), misplaced, or damaged**. 
Because the system believes stock exists:
- Automated replenishment purchase orders are **never triggered**.
- Sales quietly fall to **zero for weeks or months**.
- Store managers cannot manually count 800+ SKUs daily; they have a physical labor budget of **at most 20 checks per store-day**.

---

## 🚀 Core Product Workflow

StockSentry AI turns daily POS sales and ERP inventory signals into a focused operational loop:

$$\textbf{Detect} \longrightarrow \textbf{Rank} \longrightarrow \textbf{Explain} \longrightarrow \textbf{Investigate} \longrightarrow \textbf{Physically Verify} \longrightarrow \textbf{Record Result} \longrightarrow \textbf{Measure Impact} \longrightarrow \textbf{Learn}$$

---

## 🧠 Real AI & LLM Intelligence Capabilities

StockSentry AI features a hybrid architecture combining statistical machine learning with multi-provider generative AI:

1. **Bayesian Latent-State Anomaly Estimation**:
   - Inferences the hidden shelf availability state: $\text{Observed Sales} = \min(D^*, A^{\text{physical}})$.
   - Calibrates zero-sales persistence ($1 - e^{-\lambda N}$) against Poisson-Gamma demand baselines with day-of-week and promotional multipliers.
   - **Slow-Mover Anti-Noise Filtering**: Intermittent SKUs naturally experience zero-sales days; the model dampens suspicion scores by 55% for low-velocity items ($\lambda < 0.4$) to prevent manager fatigue.

2. **Stretch Goal: Multi-Class Signal Shape Classifier**:
   - Analyzes time-series signatures to separate:
     - **True Phantom Stock-Out**: Abrupt sales collapse while ERP records positive stock (shrinkage/theft).
     - **Misplaced on Wrong Shelf**: Intermittent micro-sales spikes in secondary aisles or backroom delay.
     - **Delisted / Discontinued SKU**: Extended zero streak (>14 days) with zero incoming warehouse replenishment and low aging stock.

3. **Multi-Provider AI Diagnostic Engine**:
   - Connects directly to:
     - **OpenAI API** (`gpt-4o`, `gpt-4o-mini`)
     - **Hugging Face Inference API** (`meta-llama/Meta-Llama-3-8B-Instruct`)
     - **Built-in Edge Neural Reasoner**: Zero-configuration, client-side expert agent running instantaneously without external API keys.
   - Produces executive root-cause analysis, failure mode probabilities, and tactical shelf inspection checklists.

4. **Interactive AI Copilot ("ShelfSentry Assistant")**:
   - Conversational assistant docked directly in the operational console.
   - Allows managers to ask queries like:
     - *"Why is SKU-104 ranked #1 today?"*
     - *"Explain the anomaly scoring formula"*
     - *"How are annual recovered rupees calculated?"*
     - *"What is the difference between phantom stock and misplaced inventory?"*

5. **Official `evaluate.py` In-Browser Engine**:
   - Direct implementation of official competition evaluation targets:
     - **Precision@20 per store-day** across all evaluated stores.
     - **Recall on hidden labels** (~3% ground-truth held-back rows).
     - Interactive threshold $N$ optimization (consecutive zero-sales days: 2 to 7).

6. **Auditable Annual Rupee Recovery Calculator**:
   - Grounded in transparent unit economics:
     $$\text{Annual ₹} = \sum_{k \in \text{Top20}} \Big[ \mathbb{I}(\text{Verified Phantom}_k) \times \mathbb{E}[\text{Daily Demand}_k] \times \text{Price}_k \times 365 \times \eta_{\text{margin}} \Big]$$
   - Real-time sensitivity sliders for margin realization factor ($\eta$) and prevented leakage duration.

7. **Synthetic Data Generation Studio**:
   - Implements the 8-step generator from the Data Strategy plan.
   - Injects **all 7 phantom mechanisms**: Shrinkage, Misplacement, Delayed ERP Adjustment, Receiving Discrepancy, Inter-Store Transfer Error, Cycle-Count Error, and Mixed Variance Drift.
   - Injects hard negatives (slow movers, promo dips, holidays).

---

## 🖥️ The 16 Operational Console Modules

| Module | Purpose |
| :--- | :--- |
| **1. Command Center (Dashboard)** | Morning overview answering: *What to check? Store risk level? Revenue at risk?* |
| **2. Morning Queue (Top 20)** | Exactly 20 ranked checks for the store manager with plain-English reasons and confidence. |
| **3. SKU Investigation** | Dual-axis time series chart (Recorded Stock vs. Daily Sales vs. Expected Demand). |
| **4. Physical Verification** | Shelf audit console with direct count stepper, simulated barcode scanner, and outcome picker. |
| **5. Feedback & History** | Ground-truth log closing the loop and feeding model calibration. |
| **6. Store Analysis** | Deep-dive location health, format, size, and category breakdown. |
| **7. All Stores Network** | 25-store chain matrix with audit compliance and risk indexing. |
| **8. Anomaly Trends** | Longitudinal tracking of recurring issues and Mean Time to Detect (MTTD). |
| **9. Rupee Recovery (ROI)** | Auditable financial quantification and interactive sensitivity analysis. |
| **10. evaluate.py Engine** | Precision@20 and hidden-label recall evaluation harness. |
| **11. Synthetic Studio** | Generates dual realities and stress-tests 7 phantom failure modes. |
| **12. Data Health** | Input contract verification and data quality audit. |
| **13. Reports & Export** | Downloadable CSVs for Top 20 queue, audit feedback, and store summaries. |
| **14. Settings** | Multi-provider AI key management (OpenAI, Hugging Face, Edge Neural). |
| **15. Help & Support** | Comprehensive operating manual, FAQ, and R1 guide. |
| **16. AI Copilot Dock** | Persistent conversational assistant for store managers. |

---

## 🛠️ Tech Stack & Architecture

- **Frontend**: Pure modern HTML5, ES6+ JavaScript, and responsive Vanilla CSS with custom properties.
- **Styling**: Tailored Dark-Slate glassmorphic theme with typography powered by *Inter* and *JetBrains Mono*.
- **Data & Models**: Local browser execution with optional external LLM API connectors (OpenAI / Hugging Face).
- **Deployment**: Static, zero-dependency bundle deployable instantly on Vercel, GitHub Pages, or any web server.

---

## 🏃 Running Locally

Serve from the repository root with any local HTTP server:

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve .
```

Then open your browser at `http://localhost:8000`.
