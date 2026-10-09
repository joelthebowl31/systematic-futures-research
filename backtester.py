"""Educational lagged close-to-close simulator; see README limitations."""
import pandas as pd

def backtest(close, signal, cost_bps=5):
    if cost_bps < 0:
        raise ValueError("cost_bps cannot be negative")
    close = close.dropna().sort_index()
    signal = signal.reindex(close.index).fillna(0)
    position = signal.shift(1).fillna(0).astype(float)
    market_return = close.pct_change().fillna(0)
    turnover = position.diff().abs().fillna(position.abs())
    strategy_return = position * market_return - turnover * cost_bps / 10000
    result = pd.DataFrame({
        "close": close, "signal": signal, "position": position,
        "market_return": market_return, "turnover": turnover,
        "strategy_return": strategy_return,
    })
    result["strategy_equity"] = (1 + strategy_return).cumprod()
    result["benchmark_equity"] = (1 + market_return).cumprod()
    return result

def backtest_next_open(open_prices, close, signal, cost_bps=5):
    """Educational next-open fill assumption; not guaranteed executable prices."""
    if cost_bps < 0:
        raise ValueError("Trading costs cannot be negative")

    df = pd.DataFrame({
        "Open": open_prices,
        "Close": close,
        "Signal": signal
    }).dropna()

    if len(df) < 2:
        raise ValueError("Not enough price data")

    df["Position"] = df["Signal"].shift(1).fillna(0)
    previous_position = df["Position"].shift(1).fillna(0)

    overnight_return = (
        df["Open"] / df["Close"].shift(1) - 1
    ).fillna(0)
    intraday_return = df["Close"] / df["Open"] - 1

    df["Trades"] = (df["Position"] - previous_position).abs()
    df["Gross_Return"] = (
        (1 + previous_position * overnight_return)
        * (1 + df["Position"] * intraday_return)
        - 1
    )
    df["Strategy_Return"] = (
        df["Gross_Return"] - df["Trades"] * cost_bps / 10000
    )
    df["Strategy_Equity"] = (1 + df["Strategy_Return"]).cumprod()
    return df
