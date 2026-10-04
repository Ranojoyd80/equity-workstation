# equity-workstation — Build Plan for Claude Code

Steps to give Claude Code in order, one session per step. Copy each prompt as written. After each step, check it against the acceptance list, then commit.

> Tip: save this file in the repo as `docs/BUILD_PLAN.md`. Claude Code can then read it, and you can say "do Step N from docs/BUILD_PLAN.md".

---

## Why this order

1. **Data first.** The charts, indicators, trade questions and watchlist all read from two tables: `trades` and `prices`. If those are wrong, everything built on them is wrong too.
2. **Backend before UI.** Each feature is an API endpoint with tests before it gets a screen. Bugs are easier to find, and Claude can later query the same endpoints.
3. **Context before chat.** "Click a trade and ask Claude" only works if the app can produce clean, compact context for a trade. Build that context endpoint first; the chat integration is then a thin layer on top.
4. **Journal before watchlist.** The journal forces the shared data layer (prices, cache, symbols) into existence. The watchlist then reuses it.

---

## Working rules (every session)

- Start each session with: *"Read CLAUDE.md and docs/BUILD_PLAN.md first."*
- Use **plan mode** (Shift+Tab) for steps that set up schemas or architecture (Steps 1, 2, 5, 7). Approve the plan before any code is written.
- End each session with: *"Run all tests, update CLAUDE.md with anything new I should know, then commit with a clear message."*
- Run `/clear` between steps. CLAUDE.md carries the important context forward.
- Never paste real account numbers into prompts. Real CSVs stay in `data/raw/` (git-ignored).
- Alpha Vantage free tier is **25 calls per day**. The app must enforce this itself.

---

## Prerequisites

- [ ] Repo set to **private** on GitHub (Settings → Danger Zone → Change visibility)
- [ ] Scaffold pushed to `main`
- [ ] Python 3.11+ and Node 20+ installed
- [ ] `.env` created from `.env.example` (Alpha Vantage key optional at first)
- [ ] One real export from **each broker** placed in `data/raw/` (Robinhood, IBKR, and any others)

---

## Step 0 — Verify the scaffold

**Prompt**
```
Read CLAUDE.md and README.md. Set up the backend venv and install the frontend
dependencies, start both servers, and confirm the frontend page shows "API: ok".
Run pytest. Fix anything that fails and explain what you changed.
```

**Acceptance**
- [ ] `http://localhost:8000/api/health` returns `{"status":"ok"}`
- [ ] `http://localhost:5173` shows "API: ok"
- [ ] `pytest` passes

---

## Step 1 — Trade importer (plan mode)

**Prompt**
```
Build a broker CSV importer in backend/app/ingest/.

Inputs: transaction exports in data/raw/ — Robinhood and IBKR to start (inspect the
real files there to learn their formats; do not print account numbers).

Normalize every equity buy/sell into a DuckDB table `trades`:
  id, account, broker, symbol, side (BUY/SELL), qty, price, fees,
  executed_at (UTC timestamp), trade_date (exchange date), currency,
  source_file, row_hash (unique)

Requirements:
- Idempotent: re-importing the same file must not create duplicates (use row_hash).
- One parser module per broker behind a common interface, so more brokers can be added later.
- Robinhood exports sometimes swap day and month. Detect and correct this
  (e.g. use the file's date ordering and impossible dates), and log every fix.
- Keep dividends, interest, transfers and fees out of `trades`. Store them in a
  separate `cash_events` table so nothing is silently dropped.
- Handle stock splits: create a `corporate_actions` table and apply split
  adjustments when computing positions (not by altering the raw rows).
- Expose POST /api/import (imports everything new in data/raw/) and a CLI:
  `python -m app.ingest data/raw/`.
- Print an import summary: rows read, inserted, skipped as duplicate, rejected (with reasons).
- Tests: build small anonymized fixture CSVs in backend/tests/fixtures/ for each broker,
  including a date-swapped Robinhood case and a duplicate import.

Show me the schema and parser design before writing code.
```

**Acceptance**
- [ ] Importing the same file twice inserts zero rows the second time
- [ ] Trade count per symbol matches your broker statements (spot-check 3 symbols)
- [ ] No impossible dates. Earliest trade is around Feb 2024
- [ ] Rejected rows are listed with reasons, not dropped silently

---

## Step 2 — Price history and cache (plan mode)

**Prompt**
```
In backend/app/market/, add a price data layer.

- A provider interface with two implementations:
  1. yfinance (free, default)
  2. Alpha Vantage TIME_SERIES_DAILY_ADJUSTED (optional, key from .env)
- DuckDB table `prices`: symbol, date, open, high, low, close, adj_close, volume, source.
- Table `api_usage`: provider, date, calls. Refuse Alpha Vantage calls once 25
  calls have been made that day, and return a clear error instead.
- Incremental fetch: for each symbol, keep data from (first trade date − 1 year)
  through the latest completed session; fetch only missing ranges.
- Symbol universe = distinct symbols in `trades` + a `watchlist_symbols` table (empty for now).
- Endpoints: GET /api/prices/{symbol}?start=&end=  and  POST /api/prices/refresh
  (optionally ?symbols=AAPL,MSFT).
- Handle delisted/renamed tickers gracefully (log and continue).
- Tests use mocked provider responses — no network calls in tests.
```

**Acceptance**
- [ ] Refresh fills every traded symbol. A second refresh fetches almost nothing
- [ ] Spot-check 3 closes against a chart site
- [ ] Alpha Vantage limit enforced (test it by setting the limit to 2 temporarily)

---

## Step 3 — Indicators and positions

**Prompt**
```
In backend/app/analysis/:

1. indicators.py — from `prices`, compute:
   - RSI(14), Wilder smoothing
   - ATR(14), Wilder smoothing
   - Relative volume = volume / 50-day average volume (exclude the current day)
   - SMA 20/50/200 for chart overlays
   Make periods parameters. Unit-test against hand-verified values.

2. positions.py — FIFO matching of `trades` into round trips:
   symbol, entry_date(s), exit_date(s), qty, avg_entry, avg_exit, fees,
   realized P&L ($ and %), holding days, R-multiple if a stop is later recorded.
   Handle partial fills, scaling in/out, and open positions. Apply splits.

3. GET /api/chart/{symbol} returns: OHLCV, indicators, the symbol's trades, and its round trips.
```

**Acceptance**
- [ ] RSI and ATR match TradingView within rounding for 2 symbols
- [ ] Realized P&L for a sample of closed trades matches your own records

---

## Step 4 — Journal chart UI

**Prompt**
```
Build the trade journal view in React using lightweight-charts.

- Symbol picker listing only symbols I've traded, searchable, showing trade count and net P&L.
- Stacked panes, time-synced (crosshair + zoom/scroll):
    1. Candles + volume (+ optional SMA 20/50/200 toggles)
    2. RSI(14) with 30/70 guides
    3. Relative volume with a 1.0 guide (and ATR as a toggleable line)
- Buy/sell markers on the price pane from my trades (buy = up arrow below bar,
  sell = down arrow above bar). Color round trips by win/loss.
- Clicking a marker opens a side panel: trade details, matched round trip, and
  RSI / ATR / relative volume on that day.
- Date-range presets: 3M, 6M, 1Y, All. Default view centers on my trades.
- Plain, clean styling. Light and dark mode.
```

**Acceptance**
- [ ] All three panes stay in sync when scrolling and zooming
- [ ] Every trade marker lands on the correct bar
- [ ] Clicking a marker shows the correct round trip

---

## Step 5 — Trade context endpoint (plan mode)

**Prompt**
```
Add GET /api/trades/{id}/context returning compact JSON for AI analysis:

- the trade and its full round trip (all fills, P&L, holding days)
- 20 sessions before entry through 20 sessions after exit: date, OHLC,
  volume, RSI, ATR, relative volume
- derived facts: entry vs 20/50/200 SMA, distance from 52-week high,
  ATR-based move during the hold, max favorable / adverse excursion (MFE/MAE)
- my other trades in the same symbol (summary only)

Keep it under ~4k tokens per trade. Also add GET /api/trades/summary
(win rate, avg win/loss, expectancy, by month and by symbol).
```

**Acceptance**
- [ ] Context for a sample trade reads clearly to you as a human
- [ ] MFE/MAE values are plausible against the chart

---

## Step 6 — Ask Claude about a trade

Two options. Prototype one, or both:

**Option A — Claude Code via MCP (no API cost beyond your plan)**
```
Create a small MCP server in backend/app/mcp/ exposing tools that wrap our API:
list_trades, get_trade_context, get_chart_data, get_trade_summary.
Register it in a project .mcp.json so Claude Code in this repo can query my
journal directly. Document usage in README.
```

**Option B — In-app chat panel (needs an Anthropic API key, usage-billed)**
```
Add a chat panel to the trade side panel. On send, the backend calls the
Anthropic API with the trade context JSON plus my question, and streams the
answer. API key from .env. Store Q&A per trade in a `trade_notes` table so
I can review past answers.
```

**Acceptance**
- [ ] Asking "why did this trade fail?" gets an answer that cites real numbers from the context

---

## Step 7 — Watchlist / research module (plan mode)

**Prompt**
```
Add a watchlist/research module that reuses the existing data layer.

- Editable named lists (create, rename, reorder, add/remove symbols),
  stored in DuckDB (`watchlists`, `watchlist_symbols`).
- Table view per list: price, % change, RSI, relative volume, short interest,
  key metrics (market cap, forward PE, PEG, FCF margin, ROIC), next earnings date.
- On-demand refresh only (a button) — no background polling. Cache results
  with a timestamp and show "as of".
- Click a row to open the same chart component from the journal (no trade markers
  unless I've traded it) plus a news list.
- Free sources first (yfinance for prices/fundamentals/earnings dates).
  Make each data field's source pluggable, so a paid provider can replace it later.
- Keyboard navigation (up/down) to scroll through companies quickly.
```

**Acceptance**
- [ ] Refreshing a 30-symbol list stays inside free-tier limits
- [ ] Each data field shows its source and "as of" time

---

## Step 8 — us-equity-analysis integration (scripts only)

**Prompt**
```
Add a user-triggered analysis runner in backend/app/analysis/equity_scoring/.

- Input: a stockanalysis.com watchlist CSV (35-column schema) dropped into data/raw/
  or uploaded through the UI.
- Implement only the data-driven parts as Python: SBC-adjusted cash metrics,
  hard gates, and the four dimension scores (Valuation, Growth, Cash Quality,
  Capital Efficiency). I'll provide the scoring rules — ask me for them first.
- Store results in `analysis_runs` and `analysis_scores` with the run timestamp.
- UI: a "Run analysis" button on a watchlist and a results table. Nothing runs automatically.
- Qualitative assessment (Competitive Position) is out of scope for now.
  Export a JSON bundle I can hand to Claude for that part.
```

**Acceptance**
- [ ] Scores match a manual run of the skill on the same CSV

---

## Later

- India equities (NSE/BSE data source, INR, separate broker parsers)
- Record stop and target levels per trade, so R-multiples get calculated
- Tag trades with setup type (breakout, pullback, etc.) and analyze results by tag
- Backup: nightly copy of the DuckDB file outside the repo
- Paid data provider, once the free prototype shows which data you actually use

---

## Quick reference

| Step | Delivers | Plan mode |
|---|---|---|
| 0 | Running scaffold | — |
| 1 | `trades`, `cash_events`, `corporate_actions` | Yes |
| 2 | `prices`, `api_usage`, refresh | Yes |
| 3 | Indicators, FIFO round trips, `/api/chart` | — |
| 4 | TradingView-style journal UI | — |
| 5 | Trade context and summary endpoints | Yes |
| 6 | Ask-Claude (MCP and/or in-app) | — |
| 7 | Watchlist / research module | Yes |
| 8 | us-equity-analysis runner | — |
