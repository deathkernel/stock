import numpy as np
import pandas as pd

def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out["close"]
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    out["rsi_14"] = 100 - (100 / (1 + rs))
    out["ema_20"] = close.ewm(span=20, adjust=False).mean()
    out["ema_50"] = close.ewm(span=50, adjust=False).mean()
    out["sma_20"] = close.rolling(20).mean()
    out["sma_50"] = close.rolling(50).mean()
    out["sma_200"] = close.rolling(200).mean()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    out["macd"] = ema12 - ema26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    mid = close.rolling(20).mean()
    std = close.rolling(20).std()
    out["bb_upper"] = mid + 2 * std
    out["bb_lower"] = mid - 2 * std
    prev_close = close.shift(1)\n    true_range = pd.concat([out["high"] - out["low"], (out["high"] - prev_close).abs(), (out["low"] - prev_close).abs()], axis=1).max(axis=1)\n    out["atr_14"] = true_range.rolling(14).mean()
    out["return_1d"] = close.pct_change()
    out["return_5d"] = close.pct_change(5)
    out["return_20d"] = close.pct_change(20)
    out["volatility_20d"] = out["return_1d"].rolling(20).std() * np.sqrt(252)
    if "volume" in out:
        out["volume_ratio_20d"] = out["volume"] / out["volume"].rolling(20).mean()
    return out
