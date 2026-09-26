from dataclasses import dataclass
import numpy as np
import pandas as pd
from backend.analytics.forecast import exponential_forecast

@dataclass
class EnsembleForecast:
    horizon: int
    point: float
    lower: float
    upper: float
    agreement: float
    models: list[str]

def ensemble_forecast(close: pd.Series, horizon: int = 5) -> EnsembleForecast:
    # v0.1 ensemble starts with a robust statistical baseline.
    # Additional ML/DL models plug into this contract without changing the API.
    baseline = exponential_forecast(close, horizon)
    recent = pd.to_numeric(close, errors="coerce").dropna()
    drift = float(recent.pct_change().tail(min(20, len(recent))).mean()) if len(recent) > 2 else 0.0
    last = float(recent.iloc[-1])
    naive_point = last * ((1 + drift) ** horizon)
    points = np.array([baseline.point, naive_point])
    point = float(points.mean())
    spread = float(np.std(points))
    interval = max(abs(point - baseline.lower), abs(baseline.upper - point), spread * 2)
    agreement = float(1 / (1 + spread / max(abs(point), 1e-9)))
    return EnsembleForecast(horizon, point, point - interval, point + interval, agreement,
                            ["exponential_smoothing", "recent_drift"])
