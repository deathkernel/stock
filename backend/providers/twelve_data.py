import httpx
import pandas as pd
from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult

class TwelveDataProvider(MarketDataProvider):
    name = "twelve_data"
    base_url = "https://api.twelvedata.com/time_series"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if not settings.twelve_data_api_key:
            raise RuntimeError("TWELVE_DATA_API_KEY is not configured")
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": min(outputsize, 5000),
            "apikey": settings.twelve_data_api_key,
        }
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()
        values = payload.get("values", [])
        df = pd.DataFrame(values)
        if not df.empty:
            df = df.rename(columns={"datetime": "date"})
            for col in ["open", "high", "low", "close", "volume"]:
                if col in df:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            df["date"] = pd.to_datetime(df["date"], utc=True)
            df = df.sort_values("date").reset_index(drop=True)
        return ProviderResult(self.name, symbol.upper(), df, {"interval": interval})
