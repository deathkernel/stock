import httpx

from backend.config import settings


class FREDClient:
    base_url = "https://api.stlouisfed.org/fred/series/observations"

    async def observations(self, series_id: str, limit: int = 30) -> list[dict]:
        if not settings.fred_api_key:
            raise RuntimeError("FRED_API_KEY is not configured")
        params = {
            "api_key": settings.fred_api_key,
            "file_type": "json",
            "series_id": series_id,
            "sort_order": "desc",
            "limit": limit,
        }
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()
        return payload.get("observations", [])

    async def market_context(self) -> dict:
        result = {}
        for name, series_id in {"vix": "VIXCLS", "fed_funds": "DFF", "ten_year": "DGS10"}.items():
            try:
                observations = await self.observations(series_id, 5)
                clean = [item for item in observations if item.get("value") not in (None, ".")]
                if clean:
                    result[name] = {"series_id": series_id, "value": float(clean[0]["value"]), "date": clean[0].get("date")}
            except Exception:
                continue
        return result
