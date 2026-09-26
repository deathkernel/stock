import httpx
from backend.config import settings

class SecEdgarClient:
    base_url = "https://data.sec.gov"

    async def company_facts(self, cik: str) -> dict:
        # SEC requests should identify the client. Set SEC_USER_AGENT in production.
        headers = {"User-Agent": settings.sec_user_agent}
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers=headers) as client:
            response = await client.get(f"{self.base_url}/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json")
            response.raise_for_status()
            return response.json()
