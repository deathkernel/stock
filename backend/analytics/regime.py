import pandas as pd
def detect_regime(df:pd.DataFrame)->dict:
    row=df.iloc[-1]; vol=float(row.get("volatility_20d",0) or 0); trend=float(row.get("trend_score",.5) or .5)
    regime="high_volatility" if vol>.40 else "bull_trend" if trend>=.75 else "bear_trend" if trend<=.25 else "range_or_mixed"
    return {"regime":regime,"volatility":vol,"trend_score":trend}
