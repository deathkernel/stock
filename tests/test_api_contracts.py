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


def test_provider_orchestrator_builds_cross_source_consensus(monkeypatch):
    import pandas as pd
    from backend.data.providers import ProviderOrchestrator
    from backend.providers.base import ProviderResult
    import backend.data.providers as providers_module

    class Provider:
        def __init__(self, name, price):
            self.name = name
            self.price = price

        async def history(self, symbol, outputsize=500):
            frame = pd.DataFrame({
                "date": pd.date_range("2026-01-01", periods=100, tz="UTC"),
                "open": [self.price] * 100,
                "high": [self.price + 1] * 100,
                "low": [self.price - 1] * 100,
                "close": [self.price] * 100,
                "volume": [1000] * 100,
            })
            return ProviderResult(self.name, symbol, frame, {})

    orchestrator = ProviderOrchestrator()
    orchestrator.providers = [Provider("one", 100), Provider("two", 101), Provider("three", 99)]
    selected, errors = __import__("asyncio").run(orchestrator.history("AAPL", 100))

    assert not errors
    consensus = selected.metadata["cross_source_consensus"]
    assert consensus["provider_count"] == 3
    assert consensus["median_last_price"] == 100.0
    assert 0.0 <= consensus["provider_agreement"] <= 1.0
