import numpy as np
import pandas as pd
from backend.analytics.regime import detect_regime
from backend.analytics.ensemble import ensemble_forecast

def regime_backtest(close:pd.Series,horizon:int=5,min_train:int=100,step:int=5)->dict:
    s=pd.to_numeric(close,errors="coerce").dropna().reset_index(drop=True)
    rows=[]
    for end in range(min_train,len(s)-horizon+1,step):
        train=s.iloc[:end]
        # Use only information available at the forecast origin.
        frame=pd.DataFrame({"close":train})
        frame["return_20d"]=frame["close"].pct_change(20)
        frame["volatility_20d"]=frame["close"].pct_change().rolling(20).std()*np.sqrt(252)
        frame["trend_score"]=float((train.iloc[-1]>=train.rolling(20).mean().iloc[-1]))
        frame["trend_score"]=0.75 if frame["trend_score"].iloc[-1] else 0.25
        regime=detect_regime(frame)["regime"]
        fc=ensemble_forecast(train,horizon)
        actual=float(s.iloc[end+horizon-1])
        base=float(s.iloc[end-1])
        rows.append({"regime":regime,"actual_return":actual/base-1,"predicted_return":fc.point/base-1,
                     "absolute_error":abs(actual-fc.point)})
    if not rows: raise ValueError("Not enough history for regime backtest")
    df=pd.DataFrame(rows)
    groups=[]
    for regime,g in df.groupby("regime"):
        groups.append({"regime":regime,"observations":len(g),"mae":float(g.absolute_error.mean()),
                       "directional_accuracy":float(np.mean(np.sign(g.actual_return)==np.sign(g.predicted_return)))})
    return {"observations":len(df),"by_regime":groups}
