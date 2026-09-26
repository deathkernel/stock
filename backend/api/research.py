from fastapi import APIRouter,HTTPException
from backend.providers.fundamentals import FundamentalsClient
from backend.news.providers import NewsClient
from backend.news.signal import aggregate_news
from backend.analytics.fundamental_features import extract_fundamental_features,fundamental_signal

router=APIRouter(prefix="/research",tags=["research"])

@router.get("/{symbol}/fundamentals")
async def fundamentals(symbol:str):
    try:
        client=FundamentalsClient(); results=[]
        for fn in (client.alpha_overview,client.finnhub_metrics):
            try: results.append(await fn(symbol.upper()))
            except Exception as exc: results.append({"error":str(exc)})
        features={}
        for r in results:
            if r.get("provider")=="alpha_vantage": features=extract_fundamental_features(r)
        return {"symbol":symbol.upper(),"sources":results,"features":features,"signal":fundamental_signal(features)}
    except Exception as exc: raise HTTPException(status_code=502,detail=str(exc))

@router.get("/{symbol}/news")
async def news(symbol:str,days:int=7):
    try:
        client=NewsClient(); items=[]
        try: items.extend(await client.finnhub_company_news(symbol.upper(),days))
        except Exception: pass
        try: items.extend(await client.alpha_news(symbol.upper(),50))
        except Exception: pass
        return {"symbol":symbol.upper(),"items":items,"aggregate":aggregate_news(items)}
    except Exception as exc: raise HTTPException(status_code=502,detail=str(exc))
