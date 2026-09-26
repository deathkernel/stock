import numpy as np

from backend.analytics.portfolio import analyze_portfolio


def test_portfolio_risk_and_correlation():
    a = np.linspace(100, 150, 180)
    b = np.linspace(100, 120, 180) + np.sin(np.arange(180)) * 2
    result = analyze_portfolio(
        [
            {"symbol": "AAA", "weight": 0.6, "close": a.tolist()},
            {"symbol": "BBB", "weight": 0.4, "close": b.tolist()},
        ],
        benchmark_close=(np.linspace(100, 140, 180)).tolist(),
    )
    assert result["observations"] > 100
    assert 0 <= result["var"] < 1
    assert 0 <= result["cvar"] < 1
    assert set(result["risk_contribution"]) == {"AAA", "BBB"}
    assert result["beta"] is not None
    assert len(result["stress_tests"]) >= 5


def test_weights_are_normalized():
    result = analyze_portfolio([
        {"symbol": "AAA", "weight": 2, "close": [100, 101, 102]},
        {"symbol": "BBB", "weight": 1, "close": [100, 99, 101]},
    ])
    assert abs(sum(result["concentration"]["weights"].values()) - 1) < 1e-9
