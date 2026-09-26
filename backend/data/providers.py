import asyncio
from statistics import median

import pandas as pd

from backend.providers.alpha_vantage import AlphaVantageProvider
from backend.providers.twelve_data import TwelveDataProvider
from backend.providers.finnhub import FinnhubProvider
from backend.providers.stooq import StooqProvider
from backend.providers.yahoo_finance import YahooFinanceProvider
from backend.providers.fmp import FMPProvider
from backend.providers.tiingo import TiingoProvider
from backend.providers.eodhd import EODHDProvider
from backend.providers.massive import MassiveProvider
from backend.data.normalize import normalize_ohlcv


class ProviderOrchestrator:
    def __init__(self):
        self.providers = [
            YahooFinanceProvider(),
            StooqProvider(),
            FMPProvider(),
            TiingoProvider(),
            EODHDProvider(),
            MassiveProvider(),
            AlphaVantageProvider(),
            TwelveDataProvider(),
            FinnhubProvider(),
        ]

    async def history(self, symbol: str, outputsize: int = 500):
        async def fetch(provider):
            try:
                result = await provider.history(symbol, outputsize=outputsize)
                result.data = normalize_ohlcv(result.data)
                if result.data.empty:
                    raise RuntimeError("provider returned an empty normalized dataset")
                return provider.name, result, None
            except Exception as exc:
                return provider.name, None, str(exc)

        results = await asyncio.gather(*(fetch(provider) for provider in self.providers))
        successes = [(name, result) for name, result, error in results if result is not None]
        errors = [
            {"provider": name, "error": error}
            for name, result, error in results
            if result is None
        ]

        if not successes:
            raise RuntimeError(f"No market data provider succeeded: {errors}")

        last_prices = [float(result.data["close"].iloc[-1]) for _, result in successes]
        consensus_price = float(median(last_prices))

        scored = []
        for name, result in successes:
            latest = float(result.data["close"].iloc[-1])
            relative_distance = abs(latest - consensus_price) / max(abs(consensus_price), 1e-9)
            agreement = max(0.0, 1.0 - min(relative_distance / 0.03, 1.0))
            completeness = min(len(result.data) / max(outputsize, 1), 1.0)
            latest_date = pd.Timestamp(result.data["date"].iloc[-1])
            now = pd.Timestamp.now(tz="UTC")
            age_days = max(0.0, (now - latest_date).total_seconds() / 86400.0)
            recency = max(0.0, 1.0 - min(age_days / 10.0, 1.0))
            score = 0.55 * agreement + 0.30 * completeness + 0.15 * recency
            scored.append((score, name, result))

        scored.sort(key=lambda item: item[0], reverse=True)
        _, selected_name, selected = scored[0]

        provider_scores = [
            {
                "provider": name,
                "score": round(float(score), 4),
                "last_price": float(result.data["close"].iloc[-1]),
                "observations": int(len(result.data)),
            }
            for score, name, result in scored
        ]

        selected.metadata = {
            **selected.metadata,
            "cross_source_consensus": {
                "providers_succeeded": [name for name, _ in successes],
                "provider_count": len(successes),
                "selected_provider": selected_name,
                "median_last_price": consensus_price,
                "relative_dispersion": round(
                    float(max(abs(price - consensus_price) for price in last_prices) / max(abs(consensus_price), 1e-9)),
                    6,
                ),
                "provider_agreement": round(
                    max(0.0, 1.0 - min((max(abs(price - consensus_price) for price in last_prices) / max(abs(consensus_price), 1e-9)) / 0.03, 1.0)),
                    4,
                ),
                "provider_scores": provider_scores,
            },
        }
        return selected, errors
