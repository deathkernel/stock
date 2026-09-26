import numpy as np
import pandas as pd
from backend.analytics.ensemble import ensemble_forecast
from backend.analytics.uncertainty import conformal_relative_interval

def rolling_calibration(close:pd.Series,horizon:int=5,min_train:int=100,step:int=5,alpha:float=.1)->dict:
    s=pd.to_numeric(close,errors="coerce").dropna().reset_index(drop=True)
    actual=[];pred=[]
    for end in range(min_train,len(s)-horizon+1,step):
        fc=ensemble_forecast(s.iloc[:end],horizon)
        actual.append(float(s.iloc[end+horizon-1]))
        pred.append(float(fc.point))
    if len(actual)<10:
        raise ValueError("At least 10 out-of-sample observations are required for calibration")
    interval=conformal_relative_interval(actual,pred,float(pred[-1]),alpha)
    coverage=float(np.mean([
        (a>=p*(1-interval["relative_error_quantile"]) and a<=p*(1+interval["relative_error_quantile"]))
        for a,p in zip(actual,pred)
    ]))
    return {
        "observations":len(actual),
        "alpha":alpha,
        "target_coverage":1-alpha,
        "empirical_coverage":coverage,
        "relative_error_quantile":interval["relative_error_quantile"],
        "lower":interval["lower"],
        "upper":interval["upper"],
    }
