# NQ opening-price and anchored-VWAP experiment

**Exploratory work in progress. No validated performance claims.**

The original script uses the label 'preregistered'; this repository contains no independent timestamped preregistration. Interpret it as a fixed candidate matrix, not proof of preregistration. Input format and timestamps must be verified before a full run. Do not combine variant results as independent trades.

NQ FAIR PRICING THEORY + ANCHORED VWAP EXPLORATORY BACKTEST

Requirements: py -m pip install numpy pandas
Script: experiments/nq_fair_pricing_backtest.py. Supply your own permitted tick data.

3 DAY TEST (Mountain time):
# Run from the repository root
py experiments/nq_fair_pricing_backtest.py --input "data/NQ 12.26 contract.txt" --input-tz America/Denver --out ".\results_NQ_FairPricing_test" --max-days 3

FULL MULTI-CONTRACT RUN:
py experiments/nq_fair_pricing_backtest.py --input "data/NQ 12-25.Last.txt" "data/NQ 03-26.Last.txt" "data/NQ 06-26.Last.txt" "data/NQ 09-26.Last.txt" "data/NQ 12.26 contract.txt" --input-tz America/Denver --out ".\results_NQ_FairPricing_all"

Tests:
- 1m, 2m, 3m, 5m; continuation and reversion; displacement and BOS confirmation.
- Opening reference: first trade >= 09:30 Eastern (07:30 Mountain).
- Reversion extensions: 25, 50, 75, 100 NQ points.
- Stops: 15, 25, 37.5, 50, 75 points; R multiples: 1.5, 2.0, 2.36; fair-price exit for valid reversions.
- Three nonmandatory anchored VWAPs: 06:30 Mountain (08:30 Eastern), NY open, and most recent qualified displacement candle (>=15 points and >=1.5x prior 20-bar median body; opposing candle displacement). Qualified displacement AVWAP is available only after the displacement candle has closed.
- 6-hour and 12-hour completed-bar bias tags included.
- Uses volume at end of semicolon NinjaTrader 'date;last;bid;ask;volume' data. If absent, assumes unit volume, which IS NOT true volume-weighted VWAP; confirm export columns.

Files:
signals.csv: selected first events per (timeframe,family,trigger,extension) each day
trades.csv.gz: all simulated stop/target/exit variants and AVWAP context tags
summary.csv: base grouped outcomes
by_contract.csv: test stability across contracts
avwap_comparison.csv: same simulated rules grouped by trade-direction-side of AVWAP, conditional sample sizes, expectancy
avwap_trade_tags.csv.gz: AVWAP features per simulated trade
first_signal_portfolio.csv, first_signal_summary.csv: one preselected earliest signal/day per bracket, NOT a fully execution-aware portfolio or Apex equity DD

IMPORTANT LIMITATIONS:
- This is a RESEARCH screening model, not a proven or live-ready strategy. The playbook leaves meaningful structure, higher-timeframe bias, and extension concepts partially subjective. These have been mechanized as described in code.
- One pass streams each local calendar day plus the previous day for swing/premarket context, not full 6-12 hours across exchange holiday/weekend gaps.
- Fair-price and AVWAP are calculated with per-tick traded price and tick volume. Candle VWAP uses summed traded-price x volume, not typical OHLC price. Session start is based on America/New_York time conversion.
- Trade execution uses next tick following signal bar, one adverse slippage tick for entry and stops, $5 round-trip per NQ contract by default. End of calendar day is used for time-stop; this can include after-hours! Next phase should enforce an explicit session flat time and trading-day boundaries.
- Multiple signals and stop/exit variants are NOT independent trades. The first-signal report does NOT account for unfilled limits (market entries are used), simultaneous portfolios, or Apex equity-trailing DD.
- Fair-price target mode is an alternative exit, not an additional trade. The premarket anchored VWAP at 06:30 MT is NOT automatically a scheduled news release. Explicit CPI/PPI/FOMC testing requires a dated release calendar.
- Historical optimal parameters are still in-sample. Pre-register a small candidate selection and verify on an untouched period before interpreting as an edge.
