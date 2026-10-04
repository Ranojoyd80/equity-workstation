# equity-workstation

Locally hosted equity workstation: a **trade journal** (historic entries/exits overlaid on price, volume, RSI, ATR, relative volume) and a **watchlist / research** module, sharing one data layer. US equities first; India later.

## Layout

```
backend/    FastAPI + DuckDB (Python 3.11+)
  app/ingest/    broker CSV transaction imports
  app/market/    price & fundamentals providers, cache
  app/analysis/  indicators and analysis scripts (user-triggered)
  app/routers/   HTTP API
frontend/   Vite + React + TypeScript, TradingView Lightweight Charts
data/       local only, git-ignored (raw CSVs, cache, database)
```

## First run

```bash
cp .env.example .env            # add API keys

# backend
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload    # http://localhost:8000/api/health

# frontend (second terminal)
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

## Data policy

Trade exports, databases and keys stay in `data/` and `.env`, both git-ignored. Do not commit personal financial data.
