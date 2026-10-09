# Systematic Futures Research — Quant Learning Portfolio

This project currently analyzes **SPY daily prices**, not ES futures. It is the first step toward systematic futures research.

## Hypothesis
Does a 20/50-day moving-average long/cash rule outperform buy-and-hold SPY over five years?

## Files
- `strategy.py`: Calculates signals.
- `backtester.py`: Calculates positions, turnover, returns, and equity curves.
- `performance.py`: Annual return, volatility, Sharpe, and maximum drawdown.
- `run_analysis.py`: Downloads SPY and compares performance.
- `tests/test_backtester.py`: Tests warmup, lagging, costs, and drawdown.

## Run in VS Code
Open this repository folder and run:

```powershell
py -m pip install -r requirements.txt
py run_analysis.py
py -m unittest discover -s tests -v
```

## Important research limitations
**This is an educational simulation, not an executable fill model.** It uses closing prices to determine signals and one-session-lagged positions for returns. This prevents applying an end-of-day signal to that same day's return, but effectively assumes a close-time fill after a close signal is computed. The next version should use *next-open execution* and model overnight and intraday returns.

Uses adjusted SPY daily prices, not futures data; assumes 5 basis points per entry/exit; no interest on cash; 0% risk-free rate for Sharpe; and 252 sessions/year. The five-year window is not held-out validation. Results do not establish a persistent edge.

## Next steps
Next-open fills, accurate trade log and open-position accounting, explicit data date range, out-of-sample validation, and a research note presenting the findings.
