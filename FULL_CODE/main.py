#!/usr/bin/env python3
"""
StockSentry AI — Official Submission Entry Point (FULL_CODE/main.py)
TalentAP Mega Hackathon 2026 · Problem R1 — The Phantom Stock-Out Detector
"""
import sys
from pathlib import Path

# Ensure ROOT and FULL_CODE are importable
ROOT = Path(__file__).resolve().parent.parent
FULL_CODE_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(FULL_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(FULL_CODE_DIR))

from FULL_CODE.pipeline.main import main

if __name__ == "__main__":
    main()

