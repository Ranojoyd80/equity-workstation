# CLAUDE.md — project notes for Claude Code

## Purpose
Single local app: trade journal + watchlist/research on a shared data layer. US equities, trade history from Feb 2024.

## Conventions
- Backend: FastAPI in `backend/app`, DuckDB file at `DB_PATH`. Run `pytest` from `backend/`.
- Frontend: Vite/React/TS in `frontend/`; charts use `lightweight-charts`. Dev server proxies `/api` to :8000.
- Indicators (RSI, ATR, relative volume) are computed server-side in `app/analysis`.
- Analysis (e.g. us-equity-analysis scoring) runs only when the user triggers it.
- Never commit anything under `data/`, any CSV, or `.env`.
- Respect the Alpha Vantage free tier (25 calls/day): cache responses in `data/cache`.
