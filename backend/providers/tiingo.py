import httpx
import pandas as pd

from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult


class TiingoProvider(MarketDataProvider):
    name = "tiingo"
    base_url = "https://api.tiingo.com/tiingo/daily"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if not settings.tiingo_api_key:
            raise RuntimeError("TIINGO_API_KEY is not configured")
        if interval not in ("1day", "1d"):
            raise RuntimeError("Tiingo provider currently supports daily data only")

        params = {
            "token": settings.tiingo_api_key,
            "startDate": "1990-01-01",
            "resampleFreq": "daily",
        }
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(f"{self.base_url}/{symbol.upper()}/prices", params=params)
            response.raise_for_status()
            payload = response.json()

        if not isinstance(payload, list):
            raise RuntimeError("Tiingo returned an unexpected response")

        df = pd.DataFrame(payload)
        if df.empty:
            raise RuntimeError(f"No Tiingo historical data found for {symbol.upper()}")

        df["date"] = pd.to_datetime(df["date"], utc=True)
        for column in ("open", "high", "low", "close", "volume"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df = df.dropna(subset=["open", "high", "low", "close"]).sort_values("date").tail(outputsize).reset_index(drop=True)
        return ProviderResult(self.name, symbol.upper(), df, {"requires_api_key": True})
