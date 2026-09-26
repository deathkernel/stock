import httpx
import pandas as pd

from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult


class EODHDProvider(MarketDataProvider):
    name = "eodhd"
    base_url = "https://eodhd.com/api/eod"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if not settings.eodhd_api_key:
            raise RuntimeError("EODHD_API_KEY is not configured")
        if interval not in ("1day", "1d"):
            raise RuntimeError("EODHD provider currently supports daily data only")

        raw = symbol.strip().upper()
        candidates = [raw]
        if "." not in raw and raw.isascii() and raw.isalnum():
            candidates.extend([f"{raw}.US", f"{raw}.NSE", f"{raw}.BSE"])

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            for ticker in candidates:
                response = await client.get(
                    f"{self.base_url}/{ticker}",
                    params={"api_token": settings.eodhd_api_key, "fmt": "json"},
                )
                if response.status_code >= 400:
                    continue
                payload = response.json()
                if not isinstance(payload, list) or not payload:
                    continue
                df = pd.DataFrame(payload)
                required = {"date", "open", "high", "low", "close", "volume"}
                if not required.issubset(df.columns):
                    continue
                df["date"] = pd.to_datetime(df["date"], utc=True)
                for column in ("open", "high", "low", "close", "volume"):
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                df = df.dropna(subset=["open", "high", "low", "close"]).sort_values("date").tail(outputsize).reset_index(drop=True)
                if not df.empty:
                    return ProviderResult(self.name, raw, df, {"eodhd_symbol": ticker, "requires_api_key": True})

        raise RuntimeError(f"No EODHD historical data found for {raw}")
