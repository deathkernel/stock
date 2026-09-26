import numpy as np
import pandas as pd

from backend.analytics.features import build_features
from backend.analytics.regime import detect_regime
from backend.analytics.confidence import confidence_score
from backend.analytics.scenarios import scenarios
from backend.analytics.fundamental_features import extract_fundamental_features
from backend.analytics.fusion_features import attach_research_features
from backend.analytics.fused_ml import train_fused_forecast


def frame(n=240):
    rng=np.random.default_rng(22)
    close=100*np.exp(np.cumsum(rng.normal(.0003,.012,n)))
    return pd.DataFrame({"date":pd.date_range("2024-01-01",periods=n),
                         "close":close,"high":close*1.01,"low":close*.99,"volume":1000})


def test_research_feature_pipeline():
    raw=frame()
    features=build_features(raw)
    fundamentals=extract_fundamental_features({
        "EPSGrowthTTMYoy":"0.12","ProfitMargin":"0.15",
        "ReturnOnEquityTTM":"0.20","QuarterlyRevenueGrowthYOY":"0.08"
    })
    fused=attach_research_features(features,fundamentals,{"sentiment":0.2,"positive":2,"negative":1})
    result=train_fused_forecast(fused,5)
    assert np.isfinite(result.point)
    assert result.observations > 0


def test_regime_confidence_and_scenarios():
    features=build_features(frame())
    regime=detect_regime(features)
    confidence=confidence_score(1,0.7,0.55,5)
    out=scenarios(100,103,0.25)
    assert regime["regime"]
    assert 0 <= confidence["score"] <= 1
    assert len(out) >= 3
