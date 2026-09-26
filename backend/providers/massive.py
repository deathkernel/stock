import httpx
import pandas as pd

from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult


class MassiveProvider(MarketDataProvider):
    name = "massive"
    base_url = "https://api.massive.com/v2"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if not settings.massive_api_key:
            raise RuntimeError("MASSIVE_API_KEY is not configured")
        if interval not in ("1day", "1d"):
            raise RuntimeError("Massive provider currently supports daily data only")

        end = pd.Timestamp.now(tz="UTC").date()
        start = end - pd.Timedelta(days=max(3650, outputsize * 3))
        url = f"{self.base_url}/aggs/ticker/{symbol.upper()}/range/1/day/{start}/{end}"
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": min(outputsize, 50000),
            "apiKey": settings.massive_api_key,
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        rows = payload.get("results") or []
        df = pd.DataFrame([{
            "date": pd.to_datetime(row.get("t"), unit="ms", utc=True),
            "open": row.get("o"),
            "high": row.get("h"),
            "low": row.get("l"),
            "close": row.get("c"),
            "volume": row.get("v"),
        } for row in rows])

        if df.empty:
            raise RuntimeError(f"No Massive historical data found for {symbol.upper()}")

        for column in ("open", "high", "low", "close", "volume"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df = df.dropna(subset=["open", "high", "low", "close"]).sort_values("date").tail(outputsize).reset_index(drop=True)
        return ProviderResult(self.name, symbol.upper(), df, {"requires_api_key": True})
