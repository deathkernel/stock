from fastapi import APIRouter, HTTPException
from backend.analytics.portfolio import analyze_portfolio
from backend.data.providers import ProviderOrchestrator

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/analyze")
def portfolio_analyze(payload: dict):
    try:
        return analyze_portfolio(
            assets=payload.get("assets", []),
            benchmark_close=payload.get("benchmark_close"),
            confidence=float(payload.get("confidence", 0.95)),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/analyze-symbols")
async def portfolio_analyze_symbols(payload: dict):
    try:
        positions = payload.get("positions", [])
        if len(positions) > 30:
            raise ValueError("A maximum of 30 portfolio positions is supported")
        if not positions:
            raise ValueError("At least one position is required")
        outputsize = min(max(int(payload.get("outputsize", 500)), 100), 2000)
        provider = ProviderOrchestrator()
        assets = []
        errors = {}
        for position in positions:
            symbol = str(position.get("symbol", "")).upper().strip()
            if not symbol:
                raise ValueError("Every position requires a symbol")
            result, provider_errors = await provider.history(symbol, outputsize)
            assets.append({
                "symbol": symbol,
                "weight": float(position.get("weight", 0)),
                "close": result.data["close"].tolist(),
            })
            if provider_errors:
                errors[symbol] = provider_errors
        benchmark = None
        benchmark_symbol = str(payload.get("benchmark", "")).upper().strip()
        if benchmark_symbol:
            result, provider_errors = await provider.history(benchmark_symbol, outputsize)
            benchmark = result.data["close"].tolist()
            if provider_errors:
                errors[benchmark_symbol] = provider_errors
        analysis = analyze_portfolio(
            assets=assets,
            benchmark_close=benchmark,
            confidence=float(payload.get("confidence", 0.95)),
        )
        analysis["provider_fallback_errors"] = errors
        return {"positions": [{"symbol": a["symbol"], "weight": a["weight"]} for a in assets],
                "benchmark": benchmark_symbol or None, "analysis": analysis}
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
