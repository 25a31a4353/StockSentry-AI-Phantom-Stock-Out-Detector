module.exports = (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { query = '', store = 'S01', sku } = req.body || {};
  const lower = query.toLowerCase();

  let response = '';

  if (lower.includes('pdf') || lower.includes('download') || lower.includes('documentation') || lower.includes('manual') || lower.includes('whitepaper')) {
    response = `### 📄 StockSentry AI — Master Project Documentation & PRD (PDF)\nA publication-quality 10-page technical manual and Product Requirements Document (PRD) is available directly from this deployment.\n\n👉 **<a href="/StockSentry_AI_Master_Documentation_and_PRD.pdf" target="_blank" download style="color:#4f46e5;font-weight:700;text-decoration:underline">Click Here to Download Master PRD & Technical Documentation PDF</a>** *(10 Pages, Publication-Grade)*\n\n* **Covers**: Executive Summary, PRD Specifications, Architecture, Poisson-Bayesian Math, Multi-Class Shapes, Rupee Recovery, 16 Modules, Store Integration, and Operator Playbook.`;
  } else if (lower.includes('video') || lower.includes('demo') || lower.includes('walkthrough') || lower.includes('recording') || lower.includes('watch')) {
    response = `### 🎥 StockSentry AI — Live Demo Video Walkthrough\nA comprehensive 3-minute video walkthrough with authentic Indian English professional voiceover and verified English subtitles (.srt & .vtt) is available.\n\n👉 **<a href="/StockSentry_AI_Live_Demo_Walkthrough.mp4" target="_blank" style="color:#4f46e5;font-weight:700;text-decoration:underline">Click Here to Watch/Download 3-Minute Live Demo Video (MP4)</a>**\n\n* **Includes**: Subtitles ([SRT](/StockSentry_AI_Live_Demo_Subtitles.srt), [VTT](/StockSentry_AI_Live_Demo_Subtitles.vtt)), real-time dashboard walkthrough, Top-20 queue, physical count reconciliation, and evaluation metrics.`;
  } else if (lower.includes('prd') || lower.includes('r1') || lower.includes('problem') || lower.includes('requirement') || lower.includes('what is phantom')) {
    response = `### 📋 Problem Statement R1 & PRD Specifications:\n* **Problem**: Identifying phantom inventory where ERP records positive stock but physical shelves are empty, blocking automated replenishment.\n* **Key Constraint**: Maximum **20 physical associate audits per store per day**.\n* **Primary Metric**: **Precision@20** optimization (>85% target).\n* **Safeguards**: Slow-moving SKUs (<0.4 units/day) are dampened by 55% to eliminate false alarms.\n* **Stretch Goal**: 3-class signal shape separation (Phantom vs Misplaced vs Delisted).`;
  } else if (lower.includes('step') || lower.includes('how to use') || lower.includes('workflow') || lower.includes('guide') || lower.includes('walkthrough')) {
    response = `### 🚀 Step-by-Step Operator Workflow:\n1. **Morning Opening (08:30 AM)**: Review Command Center KPIs for Store ${store}.\n2. **Open Morning Queue**: Prioritize the Top 20 daily items sorted by Bayesian score.\n3. **Floor Walk**: Click **Verify** next to the item on shelf and enter physical ground-truth count.\n4. **Auto-Reconciliation**: Submitting verification automatically updates the SQLite database and writes down ERP on-hand to 0.\n5. **Analytics Review**: View permanent logs in **Feedback & Learning**, evaluate Precision@20 in **evaluate.py Benchmark**, and verify ROI in **Rupee Recovery**.`;
  } else if (lower.includes('architecture') || lower.includes('tech stack') || lower.includes('backend') || lower.includes('frontend')) {
    response = `### 🏗️ StockSentry AI Technical Architecture:\n* **Frontend**: Vanilla HTML5/CSS3/ES6+ SPA with dynamic dual-theme (Dark left sidebar + Light canvas workspace) and real-time Canvas visualizations.\n* **Backend**: Serverless Edge REST API on Vercel and Python multithreaded REST server locally.\n* **Database**: Ground-truth feedback ledger with real-time ERP reconciliation.`;
  } else if (lower.includes('how') && (lower.includes('calculated') || lower.includes('score') || lower.includes('math') || lower.includes('algorithm') || lower.includes('poisson') || lower.includes('bayesian'))) {
    response = `**StockSentry AI Scoring Formula Breakdown**:\n\n1. **Zero-Sales Persistence (52%)**: Calculates Poisson probability shortfall $1 - e^{-\\lambda N}$ across $N$ consecutive zero-sales days.\n2. **Demand Gap (28%)**: Relative shortfall against expected baseline.\n3. **Stale Stock (12%)**: Penalizes static recorded inventory.\n4. **Slow-Mover Filter**: Dampens scores by 55% for items with baseline < 0.4 units/day to eliminate false alarms.`;
  } else {
    response = `### 👋 StockSentry AI Copilot (Store ${store})\nI am your retail operations assistant. You can ask me about:\n- **Master PRD (PDF)** & technical architecture\n- **3-minute live demo video** walkthrough\n- **Bayesian Poisson scoring** formula and metrics\n- **Step-by-step physical count verification** and ERP write-down\n- **Rupee recovery** calculations.`;
  }

  return res.status(200).json({ response });
};

