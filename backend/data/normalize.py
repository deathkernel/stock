import pandas as pd

REQUIRED = ["date", "open", "high", "low", "close", "volume"]

def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    missing = [c for c in REQUIRED if c not in out.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")
    out["date"] = pd.to_datetime(out["date"], utc=True)
    for col in REQUIRED[1:]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna(subset=REQUIRED).drop_duplicates("date").sort_values("date")
    out = out[(out["high"] >= out["low"]) & (out["volume"] >= 0)]
    return out.reset_index(drop=True)
