import time
import httpx
import pandas as pd

from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult


class YahooFinanceProvider(MarketDataProvider):
    """Public Yahoo Finance chart endpoint fallback; no API key required."""

    name = "yahoo_finance"
    base_url = "https://query1.finance.yahoo.com/v8/finance/chart"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if interval not in ("1day", "1d"):
            raise RuntimeError("Yahoo Finance fallback currently supports daily data only")

        raw = symbol.strip().upper()
        if not raw:
            raise RuntimeError("Symbol is required")

        # Accept common Indian symbols without a suffix.
        yahoo_symbol = raw
        if raw.isalnum() and not raw.endswith((".NS", ".BO")):
            yahoo_symbol = f"{raw}.NS"

        url = f"{self.base_url}/{yahoo_symbol}"
        params = {
            "period1": 0,
            "period2": int(time.time()),
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        }
        headers = {"User-Agent": "Mozilla/5.0 Stock-Intelligence/1.0"}

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers=headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        result = payload.get("chart", {}).get("result")
        if not result:
            error = payload.get("chart", {}).get("error") or {}
            raise RuntimeError(error.get("description") or f"No Yahoo Finance data found for {raw}")

        chart = result[0]
        timestamps = chart.get("timestamp", [])
        quote = (chart.get("indicators", {}).get("quote") or [{}])[0]
        rows = []
        for i, timestamp in enumerate(timestamps):
            row = {
                "date": pd.to_datetime(timestamp, unit="s", utc=True),
                "open": quote.get("open", [None] * len(timestamps))[i],
                "high": quote.get("high", [None] * len(timestamps))[i],
                "low": quote.get("low", [None] * len(timestamps))[i],
                "close": quote.get("close", [None] * len(timestamps))[i],
                "volume": quote.get("volume", [None] * len(timestamps))[i],
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        for column in ("open", "high", "low", "close", "volume"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df = df.dropna(subset=["open", "high", "low", "close"])
        df = df.sort_values("date").tail(outputsize).reset_index(drop=True)

        return ProviderResult(
            self.name,
            raw,
            df,
            {"source": "Yahoo Finance chart endpoint", "yahoo_symbol": yahoo_symbol, "requires_api_key": False},
        )
