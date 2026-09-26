from fastapi.testclient import TestClient
from backend.main import app

client=TestClient(app)


def test_health():
    response=client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_portfolio_validation():
    response=client.post("/api/portfolio/analyze",json={"assets":[]})
    assert response.status_code == 400


def test_status():
    response=client.get("/api/status")
    assert response.status_code == 200
    assert "portfolio" in response.json()["modules"]

def test_market_history_contract(monkeypatch):
    import pandas as pd
    from backend.providers.base import ProviderResult
    import backend.api.market as market

    class FakeProviders:
        async def history(self, symbol, outputsize=500):
            frame = pd.DataFrame({
                "date": pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True),
                "open": [100.0, 101.0],
                "high": [102.0, 103.0],
                "low": [99.0, 100.0],
                "close": [101.0, 102.5],
                "volume": [1000.0, 1200.0],
            })
            return ProviderResult("fake", symbol, frame, {}), []

    monkeypatch.setattr(market, "ProviderOrchestrator", FakeProviders)
    response = client.get("/api/market/AAPL/history?outputsize=100")
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "fake"
    assert payload["history"][0]["open"] == 100.0
    assert payload["history"][1]["close"] == 102.5
