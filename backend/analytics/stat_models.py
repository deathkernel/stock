import numpy as np
import pandas as pd
from statsmodels.tsa.ar_model import AutoReg

def autoreg_forecast(close:pd.Series,horizon:int=5,lags:int=10)->dict:
    s=pd.to_numeric(close,errors="coerce").dropna()
    if len(s)<max(80,lags*5):
        raise ValueError("Insufficient history for autoregressive forecast")
    returns=np.log(s).diff().dropna()
    model=AutoReg(returns,lags=lags,trend="ct",old_names=False).fit()
    pred=model.predict(start=len(returns),end=len(returns)+horizon-1,dynamic=False)
    cumulative=float(np.exp(np.sum(pred))-1)
    last=float(s.iloc[-1])
    point=last*(1+cumulative)
    resid_std=float(np.std(model.resid))
    interval=1.96*resid_std*np.sqrt(horizon)
    center_log=float(np.log(max(point/last,1e-12)))
    return {
        "model":"autoregressive_returns",
        "point":point,
        "lower":last*np.exp(center_log-interval),
        "upper":last*np.exp(center_log+interval),
    }
