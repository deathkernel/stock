from dataclasses import dataclass
import numpy as np
import pandas as pd
from backend.analytics.ensemble import ensemble_forecast

@dataclass
class BacktestResult:
    observations:int
    mae:float
    rmse:float
    directional_accuracy:float
    return_correlation:float
    baseline_mae:float
    improvement_vs_baseline:float

def walk_forward_backtest(close:pd.Series,horizon:int=5,min_train:int=100,step:int=5)->BacktestResult:
    s=pd.to_numeric(close,errors="coerce").dropna().reset_index(drop=True)
    actual=[];pred=[];base=[]
    for end in range(min_train,len(s)-horizon+1,step):
        train=s.iloc[:end]; fc=ensemble_forecast(train,horizon)
        actual.append(float(s.iloc[end+horizon-1])); pred.append(float(fc.point)); base.append(float(s.iloc[end-1]))
    if not actual: raise ValueError("Not enough history for walk-forward backtest")
    a,p,b=np.array(actual),np.array(pred),np.array(base)
    mae=float(np.mean(np.abs(a-p))); rmse=float(np.sqrt(np.mean((a-p)**2)))
    baseline_mae=float(np.mean(np.abs(a-b)))
    directional=float(np.mean(np.sign(a-b)==np.sign(p-b)))
    ar=a/b-1; pr=p/b-1
    corr=float(np.corrcoef(ar,pr)[0,1]) if len(ar)>1 and np.std(ar)>0 and np.std(pr)>0 else 0.0
    improvement=float(1-mae/max(baseline_mae,1e-9))
    return BacktestResult(len(a),mae,rmse,directional,corr,baseline_mae,improvement)
