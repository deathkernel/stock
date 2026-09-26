from dataclasses import dataclass
import numpy as np
import pandas as pd
from backend.analytics.forecast import exponential_forecast
from backend.analytics.stat_models import autoreg_forecast

@dataclass
class EnsembleForecast:
    horizon:int
    point:float
    lower:float
    upper:float
    agreement:float
    models:list[str]
    weights:dict

def _candidate(close,horizon):
    base=exponential_forecast(close,horizon)
    candidates=[
        {"name":"exponential_smoothing","point":float(base.point),"lower":float(base.lower),"upper":float(base.upper)},
    ]
    try:
        candidates.append(autoreg_forecast(close,horizon))
    except Exception:
        pass
    return candidates

def _walk_score(close,forecast_fn,horizon,windows=6):
    s=pd.to_numeric(close,errors="coerce").dropna().reset_index(drop=True)
    errors=[]
    start=max(80,horizon*8)
    for end in np.linspace(start,len(s)-horizon-1,windows,dtype=int):
        train=s.iloc[:end]
        try:
            p=float(forecast_fn(train,horizon)["point"])
            errors.append(abs(float(s.iloc[end+horizon-1])-p)/max(float(s.iloc[end+horizon-1]),1e-9))
        except Exception:
            continue
    return float(np.mean(errors)) if errors else np.inf

def ensemble_forecast(close:pd.Series,horizon:int=5)->EnsembleForecast:
    s=pd.to_numeric(close,errors="coerce").dropna()
    if len(s)<80:
        raise ValueError("At least 80 prices are required for ensemble forecasting")
    candidates=_candidate(s,horizon)
    errors={}
    errors["exponential_smoothing"]=_walk_score(
        s,lambda x,h: (lambda f: {"point":f.point})(exponential_forecast(x,h)),horizon)
    if any(c["name"]=="autoregressive_returns" for c in candidates):
        errors["autoregressive_returns"]=_walk_score(s,autoreg_forecast,horizon)
    finite={k:v for k,v in errors.items() if np.isfinite(v)}
    if not finite:
        weights={c["name"]:1/len(candidates) for c in candidates}
    else:
        inv={k:1/max(v,1e-8) for k,v in finite.items()}
        total=sum(inv.values())
        weights={k:v/total for k,v in inv.items()}
    for c in candidates:
        weights.setdefault(c["name"],0.0)
    point=sum(weights[c["name"]]*c["point"] for c in candidates)
    lower=min(c["lower"] for c in candidates)
    upper=max(c["upper"] for c in candidates)
    spread=float(np.sqrt(sum(weights[c["name"]]*(c["point"]-point)**2 for c in candidates)))
    lower=min(lower,point-1.96*spread)
    upper=max(upper,point+1.96*spread)
    agreement=float(1/(1+spread/max(abs(point),1e-9)))
    return EnsembleForecast(horizon,float(point),float(lower),float(upper),agreement,
                            [c["name"] for c in candidates],weights)
