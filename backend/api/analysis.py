from fastapi import APIRouter, HTTPException
from backend.analytics.backtest import walk_forward_backtest
from backend.analytics.ensemble import ensemble_forecast
from backend.analytics.features import build_features
from backend.analytics.risk import risk_metrics
from backend.data.normalize import normalize_ohlcv
from backend.data.quality import quality_report

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/pipeline")
def pipeline(payload: dict):
    try:
        import pandas as pd
        df = normalize_ohlcv(pd.DataFrame(payload["history"]))
        quality = quality_report(df)
        features = build_features(df)
        forecast = ensemble_forecast(features["close"], int(payload.get("horizon", 5)))
        risk = risk_metrics(features["close"])
        backtest = walk_forward_backtest(features["close"], int(payload.get("horizon", 5)))
        return {
            "symbol": payload.get("symbol"),
            "data_quality": quality,
            "latest_features": features.tail(1).replace({float("nan"): None}).to_dict("records")[0],
            "forecast": forecast.__dict__,
            "risk": risk,
            "backtest": backtest.__dict__,
        }
    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
