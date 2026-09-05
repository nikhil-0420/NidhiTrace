# NidhiTrace

AI-powered anomaly/irregularity detection for MPLAD Scheme implementation.
SIH 2026 - Problem Statement SIH26102 (MoSPI, Smart Automation)

## Structure
- `backend/` - FastAPI + rule engine + isolation forest + explanation layer
- `scripts/` - data cleaning/merge/validation pipeline (run in order: 01 -> 02 -> 03)
- `frontend/` - dashboard (Rithvik's build)
- `data/raw/` - drop the source CSVs here (not committed, see .gitignore)
- `docs/` - architecture notes

## Setup
1. Drop Works_Sanctioned + Works_Recommended CSVs (17th + 18th LS) into data/raw/
2. Run scripts/01, 02, 03 in order
3. `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
