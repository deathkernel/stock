import numpy as np
import pandas as pd
from backend.analytics.features import build_features
from backend.analytics.advanced_ml import evaluate_candidates,time_series_search,feature_importance

def data(n=240):
    rng=np.random.default_rng(12)
    p=100*np.exp(np.cumsum(rng.normal(.0004,.01,n)))
    return pd.DataFrame({"close":p,"high":p*1.01,"low":p*.99,"volume":1000})

def test_candidate_models():
    result=evaluate_candidates(build_features(data()),5)
    assert len(result)>=3
    assert all("mae" in x for x in result)

def test_time_series_search():
    result=time_series_search(build_features(data()),5)
    assert result["selected_config"] is not None
    assert len(result["folds"])==3

def test_feature_importance():
    result=feature_importance(build_features(data()),5)
    assert result["features"]
    assert result["observations"] > 0
    assert abs(sum(x["relative_importance"] for x in result["features"])-1) < 1e-6
