# Moving Average Strategy: Parameter Sensitivity Study

**Research status:** Exploratory  
**Asset:** SPY (S&P 500 ETF)  
**Strategy:** Long/cash moving-average crossover  
**Historical data:** Approximately 25 years downloaded; first 70% used for parameter analysis

## Research Question

Do longer-term moving-average strategies generate better risk-adjusted returns than shorter-term strategies, and how sensitive is performance to parameter selection?

## Methodology

Seven moving-average combinations were tested using historical SPY daily price data.

The strategy enters a long position when the fast moving average exceeds the slow moving average and moves to cash when the relationship reverses.

Signals are calculated using closing prices, with trades modeled at the following day's opening price. A transaction cost of five basis points is assumed for each entry or exit.

Performance was evaluated using annualized return, volatility, Sharpe ratio, maximum drawdown, and transaction frequency.

## Results

| Moving Averages | Annual Return | Sharpe Ratio | Max Drawdown | Transactions |
|---|---:|---:|---:|---:|
| 50/200 | 7.92% | 0.72 | -19.58% | 23 |
| 20/100 | 5.44% | 0.54 | -21.90% | 65 |
| 20/50 | 4.56% | 0.45 | -28.48% | 127 |
| 30/100 | 4.48% | 0.45 | -21.69% | 61 |
| 10/30 | 3.88% | 0.41 | -22.80% | 201 |
| 10/50 | 3.87% | 0.40 | -28.94% | 161 |
| 21/55 | 3.91% | 0.40 | -27.41% | 121 |

Results represent the development portion of the approximately 25-year dataset, not the entire period.

## Key Findings

**1. Longer moving averages produced stronger performance in this sample.**

The 50/200 combination generated the highest return and Sharpe ratio among the seven configurations. It also ranked first in an earlier, shorter historical experiment.

**2. Trading frequency declined substantially as moving-average periods increased.**

The 50/200 strategy generated 23 transactions compared with 127 for the 20/50 strategy and 201 for the 10/30 strategy. Lower trading frequency reduced modeled transaction-cost events, although the contribution of those savings has not been isolated.

**3. Historical period selection materially affected results.**

The 20/50 strategy generated a negative annualized return in the shorter development sample but a positive return when the historical period was extended. This highlights sensitivity to historical market environments.

**4. The evidence does not establish a persistent trading edge.**

The best-performing combination was identified after comparing seven alternatives. Its apparent advantage could reflect parameter selection, favorable market conditions, or chance.

## Limitations

- Results are historical and do not predict future performance.
- The model assumes execution at daily opening prices with fixed transaction costs, not actual observed fills.
- Cash earns no interest in the simulation.
- Sharpe ratios assume a zero risk-free rate.
- The trade sample remains small for long-term strategies.
- Portions of this historical data were previously examined during strategy development; this is not independent out-of-sample validation.
- The model uses adjusted SPY prices, not ES futures contracts.

## Preliminary Conclusion

Longer-term moving-average strategies outperformed shorter-term configurations in the tested development sample, with fewer transactions and generally stronger risk-adjusted results.

The evidence is not sufficient to conclude that the 50/200 strategy provides a repeatable advantage. Further research should separate the effects of trading costs, market exposure, and signal timing.

## Next Research Steps

1. Compare every configuration against buy-and-hold over matched dates.
2. Build rolling walk-forward training and evaluation.
3. Examine parameter sensitivity across market regimes.
4. Test sensitivity to trading-cost assumptions and cash interest.
5. Evaluate the impact of parameter selection on apparent performance.
