import pandas as pd

def detect_regime(df:pd.DataFrame)->dict:
    row=df.iloc[-1]
    vol=float(row.get("volatility_20d",0) or 0)
    trend=float(row.get("trend_score",.5) or .5)
    r20=float(row.get("return_20d",0) or 0)
    if vol>.40:
        regime="high_volatility"
    elif trend>=.75 and r20>0:
        regime="bull_trend"
    elif trend<=.25 and r20<0:
        regime="bear_trend"
    else:
        regime="range_or_mixed"
    return {"regime":regime,"volatility":vol,"trend_score":trend,"return_20d":r20}

def regime_adjustment(regime:str)->dict:
    return {
        "bull_trend":{"risk_multiplier":1.0,"confidence_penalty":0.0},
        "bear_trend":{"risk_multiplier":1.15,"confidence_penalty":0.08},
        "high_volatility":{"risk_multiplier":1.35,"confidence_penalty":0.15},
        "range_or_mixed":{"risk_multiplier":1.05,"confidence_penalty":0.04},
    }.get(regime,{"risk_multiplier":1.1,"confidence_penalty":0.1})
