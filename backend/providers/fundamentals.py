import httpx
from backend.config import settings

class FundamentalsClient:
    async def alpha_overview(self,symbol:str)->dict:
        if not settings.alpha_vantage_api_key:
            raise RuntimeError("ALPHA_VANTAGE_API_KEY is not configured")
        params={"function":"OVERVIEW","symbol":symbol.upper(),"apikey":settings.alpha_vantage_api_key}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            r=await client.get("https://www.alphavantage.co/query",params=params)
            r.raise_for_status()
            data=r.json()
        if not data or "Symbol" not in data:
            raise RuntimeError("No Alpha Vantage fundamental overview returned")
        numeric={}
        for k,v in data.items():
            try:
                numeric[k]=float(v) if v not in ("None","") else None
            except (TypeError,ValueError):
                numeric[k]=v
        return {"provider":"alpha_vantage","symbol":symbol.upper(),"data":numeric}

    async def finnhub_metrics(self,symbol:str)->dict:
        if not settings.finnhub_api_key:
            raise RuntimeError("FINNHUB_API_KEY is not configured")
        params={"symbol":symbol.upper(),"token":settings.finnhub_api_key}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            r=await client.get("https://finnhub.io/api/v1/stock/metric",params=params)
            r.raise_for_status()
            return {"provider":"finnhub","symbol":symbol.upper(),"data":r.json()}
