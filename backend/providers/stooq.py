import io
import httpx
import pandas as pd
from backend.config import settings
from backend.providers.base import MarketDataProvider, ProviderResult


class StooqProvider(MarketDataProvider):
    """Public no-key daily historical market-data fallback.

    Stooq's downloadable daily CSV endpoint is used for development and
    research fallback when keyed providers are unavailable. Symbol mapping is
    intentionally conservative: US tickers are queried as <ticker>.us.
    """

    name = "stooq"
    base_url = "https://stooq.com/q/d/l/"

    async def history(self, symbol: str, interval: str = "1day", outputsize: int = 500) -> ProviderResult:
        if interval not in ("1day", "1d"):
            raise RuntimeError("Stooq fallback currently supports daily data only")

        ticker = symbol.strip().lower()
        if not ticker or not ticker.isascii() or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789.-" for ch in ticker):
            raise RuntimeError("Unsupported symbol for Stooq fallback")

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(
                self.base_url,
                params={"s": f"{ticker}.us", "i": "d"},
            )
            response.raise_for_status()

        if response.text.strip().lower().startswith("no data"):
            raise RuntimeError(f"No Stooq daily data found for {symbol.upper()}")

        df = pd.read_csv(io.StringIO(response.text))
        required = {"Date", "Open", "High", "Low", "Close", "Volume"}
        if not required.issubset(df.columns):
            raise RuntimeError("Stooq response did not contain the expected OHLCV columns")

        df = df.rename(columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        })
        df["date"] = pd.to_datetime(df["date"], utc=True)
        for column in ("open", "high", "low", "close", "volume"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df = df.dropna(subset=["date", "open", "high", "low", "close"]).tail(outputsize).reset_index(drop=True)
        return ProviderResult(
            self.name,
            symbol.upper(),
            df,
            {"source": "Stooq public daily CSV", "requires_api_key": False},
        )
