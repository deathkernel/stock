import numpy as np
import pandas as pd

def risk_metrics(close: pd.Series) -> dict:
    returns = pd.to_numeric(close, errors="coerce").pct_change().dropna()
    if returns.empty:
        return {}
    equity = (1 + returns).cumprod()
    drawdown = equity / equity.cummax() - 1
    annualized_vol = float(returns.std() * np.sqrt(252))
    annualized_return = float((equity.iloc[-1] ** (252 / len(returns))) - 1)
    sharpe = float((returns.mean() / returns.std()) * np.sqrt(252)) if returns.std() else 0.0
    return {
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_vol,
        "max_drawdown": float(drawdown.min()),
        "sharpe": sharpe,
        "observations": int(len(returns)),
    }
