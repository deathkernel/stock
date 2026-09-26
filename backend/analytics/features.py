import pandas as pd
from backend.analytics.technical import add_technical_features

def build_features(ohlcv: pd.DataFrame) -> pd.DataFrame:
    out = add_technical_features(ohlcv)
    out["trend_score"] = (
        (out["close"] > out["ema_20"]).astype(float) * 0.25 +
        (out["ema_20"] > out["ema_50"]).astype(float) * 0.25 +
        (out["close"] > out["sma_200"]).astype(float) * 0.25 +
        (out["macd"] > out["macd_signal"]).astype(float) * 0.25
    )
    out["volatility_regime"] = pd.cut(
        out["volatility_20d"],
        bins=[-float("inf"), 0.15, 0.30, float("inf")],
        labels=["low", "normal", "high"],
    )
    return out
