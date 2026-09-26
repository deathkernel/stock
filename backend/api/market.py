from fastapi import APIRouter,HTTPException
from backend.data.providers import ProviderOrchestrator
from backend.data.quality import quality_report
from backend.analytics.features import build_features
from backend.analytics.ensemble import ensemble_forecast
from backend.analytics.backtest import walk_forward_backtest
from backend.analytics.risk import risk_metrics
from backend.analytics.regime import detect_regime
from backend.analytics.confidence import confidence_score
from backend.analytics.scenarios import scenarios
from backend.analytics.ml import train_gradient_forecast
from backend.analytics.fusion_features import attach_research_features
from backend.analytics.fused_ml import train_fused_forecast
from backend.providers.fundamentals import FundamentalsClient
from backend.news.providers import NewsClient
from backend.news.signal import aggregate_news
from backend.analytics.fundamental_features import extract_fundamental_features

router=APIRouter(prefix="/market",tags=["market"])

async def _research_inputs(symbol):
    fundamentals={}
    news_items=[]
    client=FundamentalsClient()
    try: fundamentals=extract_fundamental_features(await client.alpha_overview(symbol))
    except Exception: pass
    news=NewsClient()
    try: news_items.extend(await news.finnhub_company_news(symbol,7))
    except Exception: pass
    try: news_items.extend(await news.alpha_news(symbol,50))
    except Exception: pass
    news_agg=aggregate_news(news_items)
    return fundamentals,news_agg

@router.get("/{symbol}/research")
async def research(symbol:str,horizon:int=5,outputsize:int=500):\n    if not symbol.strip() or len(symbol.strip()) > 20:\n        raise HTTPException(status_code=400,detail="Invalid symbol")\n    if not 1 <= horizon <= 30:\n        raise HTTPException(status_code=400,detail="horizon must be between 1 and 30")\n    if not 100 <= outputsize <= 2000:\n        raise HTTPException(status_code=400,detail="outputsize must be between 100 and 2000")
    try:
        symbol=symbol.upper()
        result,errors=await ProviderOrchestrator().history(symbol,outputsize)
        f=build_features(result.data); q=quality_report(result.data)
        fundamentals,news=await _research_inputs(symbol)
        fused=attach_research_features(f,fundamentals,news)
        fc=ensemble_forecast(f["close"],horizon).__dict__; fc["last_price"]=float(f["close"].iloc[-1])
        ml=train_gradient_forecast(f,horizon).__dict__
        fused_ml=train_fused_forecast(fused,horizon).__dict__
        risk=risk_metrics(f["close"]); bt=walk_forward_backtest(f["close"],horizon); regime=detect_regime(f)
        conf=confidence_score(data_quality=q["score"],model_agreement=fc["agreement"],backtest_directional_accuracy=bt.directional_accuracy,horizon=horizon)
        history=[{"date":row["date"].isoformat() if hasattr(row["date"],"isoformat") else str(row["date"]),"close":float(row["close"])} for _,row in result.data.tail(250).iterrows()]\n        return {"symbol":symbol,"provider":result.provider,"provider_fallback_errors":errors,"data_quality":q,"history":history,
                "forecast":fc,"ml_forecast":ml,"fused_ml_forecast":fused_ml,"fundamentals":fundamentals,
                "news":news,"risk":risk,"regime":regime,"confidence":conf,
                "scenarios":scenarios(fc["last_price"],fc["point"],risk.get("annualized_volatility",0)),
                "backtest":bt.__dict__}
    except Exception as exc: raise HTTPException(status_code=502,detail=str(exc))
