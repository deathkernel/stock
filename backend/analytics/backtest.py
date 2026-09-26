from dataclasses import dataclass
import numpy as np
import pandas as pd
from backend.analytics.forecast import exponential_forecast

@dataclass
class BacktestResult:
    observations: int
    mae: float
    rmse: float
    directional_accuracy: float

def walk_forward_backtest(close: pd.Series, horizon: int = 5, min_train: int = 60, step: int = 5) -> BacktestResult:
    s = pd.to_numeric(close, errors="coerce").dropna().reset_index(drop=True)
    actual, predicted = [], []
    for end in range(min_train, len(s) - horizon + 1, step):
        train = s.iloc[:end]
        pred = exponential_forecast(train, horizon).point
        future = float(s.iloc[end + horizon - 1])
        actual.append(future)
        predicted.append(pred)
    if not actual:
        raise ValueError("Not enough history for walk-forward backtest")
    a, p = np.array(actual), np.array(predicted)
    mae = float(np.mean(np.abs(a - p)))
    rmse = float(np.sqrt(np.mean((a - p) ** 2)))
    # Compare direction against the last training price.
    base = np.array([float(s.iloc[min_train + i * step - 1]) for i in range(len(actual))])
    directional = float(np.mean(np.sign(a - base) == np.sign(p - base)))
    return BacktestResult(len(actual), mae, rmse, directional)
