# StockSentry AI — Phantom Stock-Out Detector

AI-powered retail inventory intelligence for detecting suspicious SKU–store stock mismatches and prioritizing the daily physical checks that matter most.

## Problem

A retail system can report positive inventory while the shelf is empty. That creates a **phantom stock-out**: sales stop, replenishment is not triggered, and the business may not realize inventory is physically unavailable.

## Solution

StockSentry AI turns daily sales and recorded inventory signals into a focused operational workflow:

**Detect → Rank → Explain → Verify → Record → Measure → Learn**

The core output is a daily **Top-20 “go check this shelf” queue** for each store, with confidence, evidence, reason codes, and estimated impact.

## Prototype Features

- Daily operations dashboard
- Store-level filtering
- Morning Top-20 verification queue
- SKU investigation with sales-vs-recorded-stock visualization
- Explainable anomaly reasons
- Physical verification workflow
- Verification feedback and history
- CSV export
- Reports & impact view
- Data-health and production-readiness view
- Edge-case guidance for slow-moving SKUs, promotions/holidays, and missing movement data

## R1 Evaluation Target

The supplied challenge brief defines the key evaluation targets as:

- **Precision@20 per store-day**
- **Recall on hidden labels**

The prototype UI is designed around the constraint that a manager can physically verify at most **20 SKUs per store per day**.

## Data

The current web prototype uses **illustrative demo data** shaped around the R1 brief:

- 18 months of daily sales
- ~800 SKUs
- 25 stores
- system-recorded on-hand inventory
- promotion context
- store metadata
- ~3% hidden-label evaluation setup

The demo dataset is not presented as competition ground truth. The next validation step is to wire the official supplied dataset into the scoring pipeline.

## Architecture

```text
Daily Sales + System Inventory + Promotions + Store Context
                         ↓
                 Feature Builder
                         ↓
          Expected Demand / Stock Signals
                         ↓
              Anomaly Scoring Engine
                         ↓
             Store-Day Top-20 Ranking
                         ↓
        Explainable Physical Verification Queue
                         ↓
               Manager Verification
                         ↓
               Feedback / Ground Truth
                         ↓
            Evaluation + Calibration Loop
```

## Project Status

**Prototype / product validation stage.** The interface and operational workflow are implemented. Competition-grade validation still requires the official dataset, real precision@20 and hidden-label recall calculations, edge-case testing, and auditable recovery-value calculations.

## Tech Stack

- HTML5
- CSS3
- Vanilla JavaScript
- Browser LocalStorage for prototype verification feedback
- Vercel-compatible static deployment

## Run Locally

Because this prototype is static, it can be served from the repository root with any static web server. For example:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Roadmap

1. Connect the official R1 dataset.
2. Implement reproducible feature generation and anomaly scoring.
3. Generate Top-20 rankings for every store-day.
4. Calculate precision@20 and hidden-label recall.
5. Tune thresholds against slow movers, promotions, holidays, and movement-data gaps.
6. Persist physical verification outcomes as trusted ground truth.
7. Replace illustrative impact estimates with verified lost-sales arithmetic.
8. Add production data ingestion and role-based operational workflows.
