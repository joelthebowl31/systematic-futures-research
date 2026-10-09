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
