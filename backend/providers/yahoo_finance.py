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

        candidates = [raw]
        if not raw.endswith((".NS", ".BO")) and raw.isascii() and all(ch.isalnum() or ch in "-._" for ch in raw):
            candidates.extend([f"{raw}.NS", f"{raw}.BO"])

        last_error = None
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            headers={"User-Agent": "Mozilla/5.0 Stock-Intelligence/1.0"},
        ) as client:
            for yahoo_symbol in candidates:
                response = await client.get(
                    f"{self.base_url}/{yahoo_symbol}",
                    params={
                        "period1": 0,
                        "period2": int(time.time()),
                        "interval": "1d",
                        "events": "history",
                        "includeAdjustedClose": "true",
                    },
                )
                response.raise_for_status()
                payload = response.json()
                result = payload.get("chart", {}).get("result")
                if not result:
                    last_error = (payload.get("chart", {}).get("error") or {}).get("description")
                    continue

                chart = result[0]
                timestamps = chart.get("timestamp", [])
                quote = (chart.get("indicators", {}).get("quote") or [{}])[0]
                rows = []
                for i, timestamp in enumerate(timestamps):
                    rows.append({
                        "date": pd.to_datetime(timestamp, unit="s", utc=True),
                        "open": quote.get("open", [None] * len(timestamps))[i],
                        "high": quote.get("high", [None] * len(timestamps))[i],
                        "low": quote.get("low", [None] * len(timestamps))[i],
                        "close": quote.get("close", [None] * len(timestamps))[i],
                        "volume": quote.get("volume", [None] * len(timestamps))[i],
                    })

                df = pd.DataFrame(rows)
                if df.empty:
                    last_error = f"No Yahoo Finance data found for {yahoo_symbol}"
                    continue

                for column in ("open", "high", "low", "close", "volume"):
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                df = df.dropna(subset=["open", "high", "low", "close"])
                df = df.sort_values("date").tail(outputsize).reset_index(drop=True)
                if not df.empty:
                    return ProviderResult(
                        self.name,
                        raw,
                        df,
                        {
                            "source": "Yahoo Finance chart endpoint",
                            "yahoo_symbol": yahoo_symbol,
                            "requires_api_key": False,
                        },
                    )

        raise RuntimeError(last_error or f"No Yahoo Finance data found for {raw}")
