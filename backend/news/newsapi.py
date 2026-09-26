import httpx

from backend.config import settings


class NewsAPIClient:
    base_url = "https://newsapi.org/v2/everything"

    async def company_news(self, symbol: str, company_name: str | None = None, page_size: int = 30) -> list[dict]:
        if not settings.newsapi_api_key:
            raise RuntimeError("NEWSAPI_API_KEY is not configured")

        query = symbol.upper()
        if company_name:
            query = f'"{company_name}" OR {symbol.upper()}'

        headers = {"X-Api-Key": settings.newsapi_api_key}
        params = {"q": query, "sortBy": "publishedAt", "pageSize": min(page_size, 100), "language": "en"}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers=headers) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()

        return [{
            "provider": "newsapi",
            "symbol": symbol.upper(),
            "headline": item.get("title", ""),
            "summary": item.get("description", "") or "",
            "url": item.get("url"),
            "published_at": item.get("publishedAt"),
            "source": (item.get("source") or {}).get("name"),
        } for item in payload.get("articles", [])]
