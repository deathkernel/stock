from fastapi import APIRouter,HTTPException
from backend.data.providers import ProviderOrchestrator
from backend.analytics.features import build_features
from backend.analytics.ensemble import ensemble_forecast
from backend.analytics.backtest import walk_forward_backtest
from backend.analytics.risk import risk_metrics
from backend.analytics.regime import detect_regime
from backend.analytics.confidence import confidence_score
from backend.analytics.scenarios import scenarios
router=APIRouter(prefix="/market",tags=["market"])
@router.get("/{symbol}/research")
async def research(symbol:str,horizon:int=5,outputsize:int=500):
    try:
        result,errors=await ProviderOrchestrator().history(symbol.upper(),outputsize)
        f=build_features(result.data); fc=ensemble_forecast(f["close"],horizon).__dict__; fc["last_price"]=float(f["close"].iloc[-1])
        risk=risk_metrics(f["close"]); bt=walk_forward_backtest(f["close"],horizon); regime=detect_regime(f)
        conf=confidence_score(data_quality=1.0,model_agreement=fc["agreement"],backtest_directional_accuracy=bt.directional_accuracy,horizon=horizon)
        return {"symbol":symbol.upper(),"provider":result.provider,"provider_fallback_errors":errors,"forecast":fc,"risk":risk,"regime":regime,"confidence":conf,"scenarios":scenarios(fc["last_price"],fc["point"],risk.get("annualized_volatility",0)),"backtest":bt.__dict__}
    except Exception as exc: raise HTTPException(status_code=502,detail=str(exc))
