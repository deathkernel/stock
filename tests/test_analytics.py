import pandas as pd
from backend.analytics.technical import add_technical_features
from backend.analytics.risk import risk_metrics

def test_technical_features():
    df = pd.DataFrame({
        "close": range(1, 61),
        "high": [x + 1 for x in range(1, 61)],
        "low": [max(1, x - 1) for x in range(1, 61)],
        "volume": [1000] * 60,
    })
    out = add_technical_features(df)
    assert "rsi_14" in out
    assert "sma_50" in out
    assert out["return_20d"].notna().sum() > 0

def test_risk_metrics():
    metrics = risk_metrics(pd.Series([100, 101, 99, 103, 105]))
    assert "max_drawdown" in metrics
    assert metrics["observations"] == 4
