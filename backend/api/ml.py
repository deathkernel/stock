from fastapi import APIRouter,HTTPException
import pandas as pd
from backend.analytics.features import build_features
from backend.analytics.ml import train_gradient_forecast
from backend.news.sentiment import score_headline
router=APIRouter(prefix="/ml",tags=["ml"])

@router.post("/forecast")
def ml_forecast(payload:dict):
    try:
        df=build_features(pd.DataFrame(payload["history"]))
        return train_gradient_forecast(df,int(payload.get("horizon",5)).__int__()).__dict__
    except Exception as exc: raise HTTPException(status_code=400,detail=str(exc))

@router.post("/sentiment")
def sentiment(payload:dict):
    return score_headline(str(payload.get("headline","")))
