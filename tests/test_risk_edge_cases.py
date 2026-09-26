import numpy as np
import pandas as pd
import pytest
from backend.analytics.risk import risk_metrics


def test_risk_rejects_empty():
    assert risk_metrics(pd.Series(dtype=float)) == {}


def test_risk_handles_flat_series():
    result=risk_metrics(pd.Series([100.0]*20))
    assert result["annualized_volatility"]==0.0
    assert result["sharpe"]==0.0
    assert np.isfinite(result["annualized_return"])


def test_risk_observations():
    with pytest.raises(Exception):
        risk_metrics(pd.Series([100.0]))
