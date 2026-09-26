import pandas as pd

def quality_report(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"score": 0.0, "rows": 0, "missing": True}
    required = ["date", "open", "high", "low", "close", "volume"]
    missing_ratio = float(df[required].isna().mean().mean())
    duplicate_ratio = float(df["date"].duplicated().mean())
    score = max(0.0, 1.0 - missing_ratio - duplicate_ratio)
    return {
        "score": score,
        "rows": len(df),
        "missing_ratio": missing_ratio,
        "duplicate_ratio": duplicate_ratio,
        "start": str(df["date"].min()),
        "end": str(df["date"].max()),
    }
