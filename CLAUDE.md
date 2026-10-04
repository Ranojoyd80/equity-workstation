# CLAUDE.md — project notes for Claude Code

## Purpose
Swing Decision Lab: are my swing-trade decisions random, or is there a repeatable, learnable pattern?
**Read `docs/OBJECTIVE.md` first.** It is the source of truth for scope and method. `BUILD_PLAN.md` is superseded wherever the two conflict (watchlist, fundamentals scoring, R-multiples and Alpha Vantage are out of scope).

## Scope in one breath
US-equity swing trades since Jan 2024 (IBKR, Fidelity, Robinhood). Swing trade = flat-to-flat round trip held 2–30 calendar days with total buys ≥ $5,000 (locked; never tune after seeing results). GOOG/GOOGL = one name. Currently 61 trips, 31 names. Every buy/add/sell is a scored *decision*. Decisions are compared with a random-timing benchmark and grouped by four fixed conditions. Patterns are discovered on older trades and confirmed on newer ones. Keep the app small; no heavy technical analysis.

## Conventions
- Backend: FastAPI in `backend/app`, DuckDB file at `DB_PATH`. Run `pytest` from `backend/`.
- Frontend: Vite/React/TS in `frontend/`; charts use `lightweight-charts`. Dev server proxies `/api` to :8000. (Whether to keep this stack is still open; see OBJECTIVE.md.)
- All indicators and scores are computed locally, never fetched.
- Analysis runs only when the user triggers it.
- Never commit anything under `data/`, any CSV/XLSX, or `.env`. Test fixtures are built in code, not as CSV files.
- Never print account numbers or dollar amounts from real broker files when inspecting them.

## Data rules
- Pooled book, FIFO per ticker per book. Each account has a default book (swing / long-term), and `book_overrides` holds per-fill exceptions keyed by row_hash.
- Long only. A sell larger than the position held is a data error (missing pre-2024 lot, transfer-in, missing split): reject it and give the reason; never treat it as a short.
- Trade = flat-to-flat per ticker per book. Decisions are the individual fills.
- Robinhood exports can swap day and month: detect, correct and log every fix.
- Store raw fill prices plus a split-adjustment factor; charts use split-adjusted bars.
- Prices: yfinance daily OHLCV and splits (backup Stooq/Tiingo), cached locally. 30-minute bars are for viewing only (~60 days available free).

## Definitions — do not re-derive these differently
- **RSI(14):** Wilder/RMA smoothing seeded with an SMA (matches TradingView). Signal line = SMA(14) of RSI.
- **ATR(14):** Wilder/RMA of true range. ATR is the unit for every move and score.
- **Volume level:** decision-day volume ÷ median of the prior 20 sessions (excluding the day itself). Heavy ≥ 1.5, Quiet < 0.7, otherwise Normal. If weekly bars are ever added, recompute from weekly volume; never average down from daily.
- **Support/resistance zones as of date D:** 5-bar swing pivots (high/low beats 5 bars on each side), usable only once confirmed (pivot index + 5 ≤ D); 1-year (252-session) lookback; pivots within 0.5 × ATR(D) merge into one zone; strength = touch count. Never use data after D.
- **Range position:** Near ceiling = within 0.5 ATR below a resistance zone (or inside it); Near floor = within 0.5 ATR above support; Breakout = close above a resistance zone within the last 3 sessions; otherwise Mid-range.
- **RSI level:** daily RSI(14) ≥ 70 / 30–70 / ≤ 30.
- **What the move rests on:** user tag: company-specific / external / nothing notable. Pre-fill company-specific if earnings fell in the prior 10 sessions.
- **Decision score:** value against holding at +5/+10/+20 sessions, in ATR(D) multiples. For sells, a positive score means the sale beat holding; for buys, it means the entry beat waiting.
- **Shuffle test:** re-score each decision on random days within ±5 sessions (thousands of runs). Report "random timing did as well X% of the time".
- **Small samples:** always show n; groups below the agreed minimum are shown as cases, not statistics.
