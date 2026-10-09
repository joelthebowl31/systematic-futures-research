"""Annualized performance metrics assuming 252 sessions and 0% risk-free."""
import numpy as np

def summarize(returns, annual_periods=252):
    if returns.empty:
        raise ValueError("No returns supplied")
    equity = (1 + returns).cumprod()
    annual_return = (equity.iloc[-1] ** (annual_periods / len(returns)) - 1
                     if equity.iloc[-1] > 0 else float("nan"))
    volatility = returns.std() * np.sqrt(annual_periods)
    sharpe = (returns.mean() / returns.std() * np.sqrt(annual_periods)
              if returns.std() > 0 else float("nan"))
    drawdown = equity / equity.cummax() - 1
    return dict(annual_return=annual_return, volatility=volatility,
                sharpe=sharpe, max_drawdown=drawdown.min())
