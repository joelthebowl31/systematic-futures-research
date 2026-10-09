"""Download SPY and compare educational close-to-close and next-open models."""
import matplotlib.pyplot as plt
import yfinance as yf
from strategy import moving_average_signal
from backtester import backtest, backtest_next_open
from performance import summarize

def main():
    data = yf.download("SPY", period="5y", interval="1d",
                       auto_adjust=True, progress=False)
    if data.empty:
        raise RuntimeError("No SPY data returned")
    open_prices = data["Open"].squeeze()
    close = data["Close"].squeeze().dropna()
    signal = moving_average_signal(close, 20, 50)
    result = backtest(close, signal, cost_bps=5)
    open_result = backtest_next_open(open_prices, close, signal, cost_bps=5)

    print("Educational simulations, not guaranteed executable fills.")
    for label, returns in [
        ("Original MA strategy", result["strategy_return"]),
        ("SPY buy-and-hold", result["market_return"]),
        ("Next-open MA strategy", open_result["Strategy_Return"])
    ]:
        stats = summarize(returns)
        print("\n" + label)
        print(f"Annual return: {stats['annual_return']:.2%}")
        print(f"Volatility: {stats['volatility']:.2%}")
        print(f"Sharpe (0% RF): {stats['sharpe']:.2f}")
        print(f"Max drawdown: {stats['max_drawdown']:.2%}")

    print(f"\nTime invested: {result['position'].mean():.1%}")
    print(f"Entries and exits: {int(result['turnover'].sum())}")
    plt.figure(figsize=(12, 6))
    plt.plot(result.index, result["strategy_equity"], label="Original MA")
    plt.plot(open_result.index, open_result["Strategy_Equity"], label="Next-open MA")
    plt.plot(result.index, result["benchmark_equity"], label="SPY buy-and-hold")
    plt.title("SPY Moving Average Backtest Comparison")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
