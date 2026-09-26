import httpx
import pandas as pd
from backend.config import settings

class NewsClient:
    async def finnhub_company_news(self,symbol:str,days:int=7)->list[dict]:
        if not settings.finnhub_api_key:
            raise RuntimeError("FINNHUB_API_KEY is not configured")
        end=pd.Timestamp.now(tz="UTC").date()
        start=(pd.Timestamp.now(tz="UTC")-pd.Timedelta(days=days)).date()
        params={"symbol":symbol.upper(),"from":str(start),"to":str(end),"token":settings.finnhub_api_key}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            r=await client.get("https://finnhub.io/api/v1/company-news",params=params)
            r.raise_for_status()
            data=r.json()
        return [{"provider":"finnhub","symbol":symbol.upper(),"headline":x.get("headline",""),
                 "summary":x.get("summary",""),"url":x.get("url"),
                 "published_at":pd.to_datetime(x.get("datetime"),unit="s",utc=True).isoformat() if x.get("datetime") else None,
                 "source":x.get("source"),"category":x.get("category")} for x in data]

    async def alpha_news(self,symbol:str,limit:int=50)->list[dict]:
        if not settings.alpha_vantage_api_key:
            raise RuntimeError("ALPHA_VANTAGE_API_KEY is not configured")
        params={"function":"NEWS_SENTIMENT","tickers":symbol.upper(),"limit":limit,"apikey":settings.alpha_vantage_api_key}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            r=await client.get("https://www.alphavantage.co/query",params=params)
            r.raise_for_status()
            data=r.json()
        return [{"provider":"alpha_vantage","symbol":symbol.upper(),"headline":x.get("title",""),
                 "summary":x.get("summary",""),"url":x.get("url"),
                 "published_at":x.get("time_published"),
                 "source":x.get("source"),
                 "sentiment_score":x.get("overall_sentiment_score"),
                 "sentiment_label":x.get("overall_sentiment_label")} for x in data.get("feed",[])]
