from dataclasses import dataclass
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

@dataclass
class Forecast:
    horizon: int
    point: float
    lower: float
    upper: float
    method: str

def exponential_forecast(close: pd.Series, horizon: int = 5) -> Forecast:
    series = pd.to_numeric(close, errors="coerce").dropna()
    if len(series) < 30:
        raise ValueError("At least 30 observations are required for forecasting")
    model = ExponentialSmoothing(series, trend="add", seasonal=None).fit(optimized=True)
    pred = model.forecast(horizon)
    point = float(pred.iloc[-1])
    residual = float(np.nanstd(model.resid))
    lower = point - 1.96 * residual
    upper = point + 1.96 * residual
    return Forecast(horizon, point, lower, upper, "exponential_smoothing")
