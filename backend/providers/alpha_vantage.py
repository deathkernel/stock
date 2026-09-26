import httpx
import pandas as pd
from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult

class AlphaVantageProvider(MarketDataProvider):
    name = "alpha_vantage"
    base_url = "https://www.alphavantage.co/query"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if not settings.alpha_vantage_api_key:
            raise RuntimeError("ALPHA_VANTAGE_API_KEY is not configured")
        function = "TIME_SERIES_DAILY"
        params = {
            "function": function,
            "symbol": symbol,
            "outputsize": "full" if outputsize > 100 else "compact",
            "apikey": settings.alpha_vantage_api_key,
        }
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()
        series = payload.get("Time Series (Daily)", {})
        rows = [
            {"date": date, "open": float(v["1. open"]), "high": float(v["2. high"]),
             "low": float(v["3. low"]), "close": float(v["4. close"]), "volume": float(v["5. volume"])}
            for date, v in series.items()
        ]
        df = pd.DataFrame(rows)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], utc=True)
            df = df.sort_values("date").tail(outputsize).reset_index(drop=True)
        return ProviderResult(self.name, symbol.upper(), df, {"function": function})
