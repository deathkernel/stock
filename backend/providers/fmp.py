import httpx
import pandas as pd

from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult


class FMPProvider(MarketDataProvider):
    name = "financial_modeling_prep"
    base_url = "https://financialmodelingprep.com/stable/historical-price-eod/full"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if not settings.fmp_api_key:
            raise RuntimeError("FMP_API_KEY is not configured")
        if interval not in ("1day", "1d"):
            raise RuntimeError("FMP provider currently supports daily data only")

        params = {"symbol": symbol.upper(), "apikey": settings.fmp_api_key}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()

        if not isinstance(payload, list):
            raise RuntimeError("FMP returned an unexpected response")

        df = pd.DataFrame([{
            "date": row.get("date"),
            "open": row.get("open"),
            "high": row.get("high"),
            "low": row.get("low"),
            "close": row.get("close"),
            "volume": row.get("volume"),
        } for row in payload])

        if df.empty:
            raise RuntimeError(f"No FMP historical data found for {symbol.upper()}")

        df["date"] = pd.to_datetime(df["date"], utc=True)
        for column in ("open", "high", "low", "close", "volume"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df = df.dropna(subset=["open", "high", "low", "close"]).sort_values("date").tail(outputsize).reset_index(drop=True)
        return ProviderResult(self.name, symbol.upper(), df, {"requires_api_key": True})
