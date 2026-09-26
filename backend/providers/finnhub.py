import httpx
import pandas as pd
from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult

class FinnhubProvider(MarketDataProvider):
    name = "finnhub"
    base_url = "https://finnhub.io/api/v1"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if not settings.finnhub_api_key:
            raise RuntimeError("FINNHUB_API_KEY is not configured")
        # Finnhub uses UNIX timestamps for candle history.
        end = int(pd.Timestamp.now(tz="UTC").timestamp())
        start = int((pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=max(365, outputsize * 2))).timestamp())
        params = {"symbol": symbol, "resolution": "D", "from": start, "to": end, "token": settings.finnhub_api_key}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(f"{self.base_url}/stock/candle", params=params)
            response.raise_for_status()
            payload = response.json()
        if payload.get("s") != "ok":
            return ProviderResult(self.name, symbol.upper(), pd.DataFrame(), {"status": payload.get("s")})
        df = pd.DataFrame({
            "date": pd.to_datetime(payload["t"], unit="s", utc=True),
            "open": payload["o"], "high": payload["h"], "low": payload["l"],
            "close": payload["c"], "volume": payload["v"],
        }).sort_values("date").tail(outputsize).reset_index(drop=True)
        return ProviderResult(self.name, symbol.upper(), df, {"status": "ok"})
