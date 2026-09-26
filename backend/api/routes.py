from fastapi import APIRouter, HTTPException
from backend.analytics.decision import decision_snapshot
from backend.analytics.risk import risk_metrics

router = APIRouter()

@router.get("/status")
def status():
    return {"status": "ready", "modules": ["providers", "technical", "forecast", "risk", "portfolio", "decision"]}

@router.post("/decision")
def decision(payload: dict):
    try:
        return decision_snapshot(
            forecast_return=float(payload.get("forecast_return", 0)),
            volatility=float(payload.get("volatility", 0)),
            trend_score=float(payload.get("trend_score", 0.5)),
            data_quality=float(payload.get("data_quality", 1)),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/risk")
def risk(payload: dict):
    try:
        return risk_metrics(payload["close"])
    except KeyError:
        raise HTTPException(status_code=400, detail="close series is required")
