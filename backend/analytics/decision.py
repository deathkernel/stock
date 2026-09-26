def decision_snapshot(*, forecast_return: float, volatility: float, trend_score: float, data_quality: float = 1.0) -> dict:
    # Research classification only: not a trading recommendation.
    confidence = max(0.0, min(1.0, data_quality * (1.0 - min(volatility, 1.0) * 0.35)))
    if forecast_return > 0.02 and trend_score > 0.55:
        outlook = "positive"
    elif forecast_return < -0.02 and trend_score < 0.45:
        outlook = "negative"
    else:
        outlook = "mixed"
    return {
        "outlook": outlook,
        "forecast_return": forecast_return,
        "confidence": confidence,
        "volatility": volatility,
        "research_only": True,
    }
