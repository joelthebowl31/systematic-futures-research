# Systematic Trading & Digital Asset Research
**Joel Hugentobler | Research and product strategy portfolio**

I use research to turn an interesting idea into a testable question, an explicit model, and a decision. This portfolio combines systematic trading experiments with digital asset business-model analysis.

## Start here
| Project | Question | What to inspect |
|---|---|---|
| [Variational economics](research/variational_case_study.md) | Can revenue growth mask weaker economics in the business supporting it? | Economic model, sensitivity, and product implications |
| [SPY moving-average study](research/moving_average_study.md) | How sensitive are historical results to parameter choice? | Research note and tested simulation code |
| [NQ opening-price experiment](experiments/README.md) | How do continuation/reversion hypotheses behave under explicit execution assumptions? | Tick-data script and research limitations |

## My contribution and use of AI
I frame the research questions, choose assumptions, run experiments, interpret results, and decide which questions deserve further investigation. I use AI assistance to develop and debug Python code. This is a research portfolio and a record of learning, not a claim of production engineering experience or verified trading profitability.

## Run the SPY demonstration
Python 3.10+:
```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m unittest discover -s tests -v
```

The runner downloads a rolling five-year window of adjusted SPY prices and compares buy-and-hold with a 20/50 moving-average long/cash rule. It includes both a legacy lagged close-to-close approximation and a next-open simulation separating overnight from intraday returns. Neither guarantees executable fills.

The linked parameter study records an earlier, longer-history experiment. The default runner does **not** reproduce that seven-parameter table. Exact source data and run metadata for that study are not bundled; the recorded figures have not been independently reproduced here.

## Research discipline
- State the hypothesis and assumptions before interpreting outcomes.
- Check signal timing, costs, and execution semantics.
- Treat parameter sweeps as exploratory; correlated variants are not independent evidence.
- Distinguish a useful model from a validated investment or trading decision.
- Report limitations and what would change the conclusion.

## Scope and limitations
SPY is an ETF, not a futures contract. The SPY simulations use five basis points per entry/exit, no interest on cash, a zero risk-free rate for Sharpe, and 252 sessions/year. NQ assumptions differ and are documented separately. Historical exploration is not held-out validation. Raw market data, brokerage records, and confidential client work are not included.

## Next steps
Reproducible dated datasets where redistribution is permitted; matched-period benchmarks; explicit futures session boundaries; cost and regime sensitivity; and genuinely untouched evaluation periods.

