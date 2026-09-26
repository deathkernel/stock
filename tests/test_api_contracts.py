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
