from fastapi import APIRouter,HTTPException
from backend.analytics.ml import train_gradient_forecast
from backend.analytics.advanced_ml import evaluate_candidates,time_series_search
from backend.news.sentiment import score_headline

router=APIRouter(prefix="/ml",tags=["ml"])

@router.post("/forecast")
def forecast(payload:dict):
    try:
        import pandas as pd
        df=pd.DataFrame(payload["history"])
        horizon=int(payload.get("horizon",5))
        return train_gradient_forecast(df,horizon).__dict__
    except Exception as exc:
        raise HTTPException(status_code=400,detail=str(exc))

@router.post("/candidates")
def candidates(payload:dict):
    try:
        import pandas as pd
        return {"models":evaluate_candidates(pd.DataFrame(payload["history"]),int(payload.get("horizon",5)))}
    except Exception as exc:
        raise HTTPException(status_code=400,detail=str(exc))

@router.post("/search")
def search(payload:dict):
    try:
        import pandas as pd
        return time_series_search(pd.DataFrame(payload["history"]),int(payload.get("horizon",5)))
    except Exception as exc:
        raise HTTPException(status_code=400,detail=str(exc))

@router.post("/sentiment")
def sentiment(payload:dict):
    return score_headline(payload.get("headline",""))
