"""Download data and run the first SPY moving-average experiment."""
import matplotlib.pyplot as plt
import yfinance as yf
from strategy import moving_average_signal
from backtester import backtest
from performance import summarize

def main():
    data = yf.download("SPY", period="5y", interval="1d",
                       auto_adjust=True, progress=False)
    if data.empty:
        raise RuntimeError("No SPY data returned")
    close = data["Close"].squeeze().dropna()
    result = backtest(close, moving_average_signal(close, 20, 50), cost_bps=5)
    print("EDUCATIONAL SIMULATION: not realistic next-open fills")
    for label, column in [("MA strategy", "strategy_return"),
                          ("SPY buy-and-hold", "market_return")]:
        stats = summarize(result[column])
        print("\n" + label)
        print(f"Annual return: {stats['annual_return']:.2%}")
        print(f"Volatility: {stats['volatility']:.2%}")
        print(f"Sharpe (0% RF): {stats['sharpe']:.2f}")
        print(f"Max drawdown: {stats['max_drawdown']:.2%}")
    print(f"\nTime invested: {result['position'].mean():.1%}")
    print(f"Entries and exits: {int(result['turnover'].sum())}")
    result[["strategy_equity", "benchmark_equity"]].plot(
        title="SPY Moving Average vs Buy-and-Hold")
    plt.ylabel("Growth of $1")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
