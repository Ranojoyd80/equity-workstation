# Objective — Swing Decision Lab

Agreed 2026-10-04. This supersedes `BUILD_PLAN.md` wherever they conflict.

## The question
**Are my swing-trade decisions random, or is there a repeatable, learnable pattern?**
The app answers this from my own trades, with evidence. Where the evidence is too thin, it says so.

## Scope
- **In:** swing trades in US equities since Jan 2024, across IBKR, Fidelity and Robinhood.
- **Swing trade (locked 2026-10-04, before any results were seen):** a flat-to-flat round trip held **2–30 calendar days**, with **total buys of at least $5,000**. Same-day trips, 1-day trips, holds over 30 days, and trips with no matching buy on record are excluded. GOOG and GOOGL count as one name. With these rules the data has 61 trips across 31 names (2024: 27, 2025: 6, 2026: 28). A smaller list of focus names may be set next; it must also be fixed before scoring.
- **Out (for now):** long-term holdings, the watchlist, fundamentals scoring, tax, India, heavy technical analysis, and anything intraday in the scoring.

## Core ideas
- **Decision:** a single buy, add, partial sell or final sell. Each decision is scored on its own, which gives roughly 80–150 decisions.
- **Trade:** from flat back to flat, per ticker, within the swing book. It groups decisions for display.
- **Random benchmark:** what a random decision would have scored in the same spot. Skill means beating it consistently.
- **Conditions:** four things I actually look at, fixed in advance (see below). Decisions are grouped by them to find patterns.
- **Rule book:** patterns that hold up become named rules, marked *candidate*, *confirmed* or *retired*. A rule can be retired for one ticker only. Revisions are kept, including why a rule was wrong.

## Method
1. **Score each decision against holding** at fixed horizons of 5, 10 and 20 sessions, in ATR multiples. For sells, a positive score means the sale beat holding. For buys, it means the entry beat waiting. Fixed horizons stop a closed decision from being re-marked every day.
2. **Shuffle test:** move each decision to a random day within ±5 sessions and re-score it, thousands of times. The answer in plain words: *"random timing did as well as you X% of the time."*
3. **Pooled verdict first:** are my sells better than random, and are my buys? These are answered separately.
4. **Then one condition at a time:** for example, are sells near a ceiling better than random? Pairs of conditions are checked only for the one or two most promising cases, never all combinations.
5. **Discover, then confirm:** patterns are found in older trades (cut-off around end of 2025, fixed once the data is loaded). They count as real only if they hold in newer trades. Patterns that fail are retired.
6. **Learnable** means the edge holds across years and names, and decisions improve after a rule is adopted.
7. **Small samples are flagged:** every result shows n, and a group with few decisions is shown as cases, not as a statistic.

## The four conditions
| Condition | Levels | Definition |
|---|---|---|
| Range position | Near ceiling · Near floor · Breakout · Mid-range | Daily support/resistance zones known on that date: 5-bar swing pivots confirmed 5 sessions later, merged within 0.5 ATR, 1-year lookback. "Near" means within 0.5 ATR. Breakout means a close above resistance in the last 3 sessions. |
| Volume | Heavy ≥1.5× · Normal · Quiet <0.7× | Decision-day volume against the median of the prior 20 sessions. |
| RSI | ≥70 · 30–70 · ≤30 | Daily RSI(14), Wilder smoothing (matches TradingView). |
| What the move rests on | Company-specific · External · Nothing notable | Tagged by me. Pre-filled as company-specific when earnings fell within the prior 10 sessions. |

## What the app shows
1. **Verdict:** sells vs random and buys vs random, each with n, plus how the verdict has changed as trades were added.
2. **Conditions:** one table per condition, showing each group's score against random, with n.
3. **Cases:** every decision in a group side by side, in the style of the LITE/COIN review.
4. **Rule book:** rules with their status, evidence and history.
5. **Decision view:** one clean chart with decision markers and the levels as of that date. It uses 30-minute bars where available and daily bars otherwise.

## Data
- **Fills:** broker exports (CSV or Excel) from IBKR, Fidelity and Robinhood. Robinhood needs its day/month swap fixed.
- **Book:** one pooled book with FIFO per ticker. Each account has a default book (swing or long-term), with per-fill overrides on the few tickers that are in both. Long only: a sell larger than the position held is a data error.
- **Prices:** free sources only. Daily OHLCV and splits from yfinance, with Stooq or Tiingo as backup, cached locally. 30-minute bars are for viewing only, about the last 60 days.
- **Raw prices:** raw fill prices are stored with a split-adjustment factor. Indicators are calculated locally.

## Done when
I can open the app and see, with honest confidence levels: whether my sells and buys beat random timing; which of the four conditions, if any, separates good decisions from bad ones; and the cases behind each answer.

## Open
- Sample exports from each broker. This is the blocker for building.
- Exact discover/confirm cut-off date, set once trades are loaded.
- Whether to keep the existing FastAPI + React scaffold or build something smaller. To be decided at design time.
