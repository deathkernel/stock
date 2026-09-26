from fastapi import APIRouter, HTTPException
from backend.analytics.portfolio import analyze_portfolio

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/analyze")
def portfolio_analyze(payload: dict):
    try:
        assets = payload.get("assets", [])
        return analyze_portfolio(
            assets=assets,
            benchmark_close=payload.get("benchmark_close"),
            confidence=float(payload.get("confidence", 0.95)),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
