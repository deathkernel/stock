import numpy as np
import pandas as pd
from backend.analytics.ensemble import ensemble_forecast
from backend.analytics.backtest import walk_forward_backtest
from backend.analytics.ml import train_gradient_forecast
from backend.analytics.features import build_features

def synthetic_prices(n=220):
    rng=np.random.default_rng(7)
    returns=rng.normal(0.0005,0.012,n)
    return pd.Series(100*np.exp(np.cumsum(returns)))

def test_ensemble_has_finite_interval():
    fc=ensemble_forecast(synthetic_prices(),5)
    assert np.isfinite(fc.point)
    assert fc.lower < fc.upper
    assert 0 <= fc.agreement <= 1

def test_walk_forward_has_baseline():
    bt=walk_forward_backtest(synthetic_prices(),5,min_train=120,step=10)
    assert bt.observations > 0
    assert bt.baseline_mae >= 0
    assert -1 <= bt.return_correlation <= 1

def test_ml_selection():
    prices=synthetic_prices()
    raw=pd.DataFrame({"close":prices,"high":prices*1.01,"low":prices*.99,"volume":1000})
    features=build_features(raw)
    result=train_gradient_forecast(features,5)
    assert result.model in {"hist_gradient_boosting","random_forest"}
    assert np.isfinite(result.point)
