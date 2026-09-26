"""Explainable quantitative research signal.

The score is a research classification, not a guaranteed trading outcome.
"""


def _clip(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, float(value)))


def _signed_score(value: float, scale: float) -> float:
    # Maps a raw signal to [-1, 1] while keeping extreme values bounded.
    import math
    return math.tanh(float(value) / max(scale, 1e-9))


def decision_snapshot(
    *,
    last_price: float,
    forecast_price: float,
    trend_score: float,
    directional_accuracy: float,
    data_quality: float = 1.0,
    news_sentiment: float = 0.0,
    ml_prices: list[float] | None = None,
    volatility: float = 0.0,
    source_agreement: float = 1.0,
) -> dict:
    """Build a transparent BUY/SELL/HOLD research signal.

    Components:
      forecast_return 30%
      trend            20%
      model_consensus  20%
      validation       15%
      sentiment        10%
      source agreement   5%
      data quality       5%

    Volatility attenuates conviction rather than changing the raw direction.
    """

    import math

    last = max(float(last_price), 1e-9)
    forecast = float(forecast_price)
    forecast_return = forecast / last - 1.0

    forecast_signal = _signed_score(forecast_return, 0.03)
    trend_signal = _clip(2.0 * float(trend_score) - 1.0, -1.0, 1.0)
    validation_strength = _clip((float(directional_accuracy) - 0.50) / 0.25, -1.0, 1.0)
    sentiment_signal = _clip(float(news_sentiment) / 0.35, -1.0, 1.0)

    model_values = [float(x) for x in (ml_prices or []) if x is not None and math.isfinite(float(x))]
    model_signals = [
        _signed_score(value / last - 1.0, 0.03)
        for value in model_values
    ]
    model_consensus = sum(model_signals) / len(model_signals) if model_signals else forecast_signal

    raw_score = (
        0.30 * forecast_signal
        + 0.20 * trend_signal
        + 0.20 * model_consensus
        + 0.15 * validation_strength
        + 0.10 * sentiment_signal
        + 0.05 * _clip(2.0 * float(source_agreement) - 1.0, -1.0, 1.0)
        + 0.05 * _clip(2.0 * float(data_quality) - 1.0, -1.0, 1.0)
    )

    volatility_penalty = _clip(max(float(volatility) - 0.20, 0.0) / 0.80, 0.0, 1.0)
    conviction = abs(raw_score) * (1.0 - 0.30 * volatility_penalty)
    conviction = _clip(conviction, 0.0, 1.0)
    score = _clip(50.0 + raw_score * 50.0, 0.0, 100.0)

    if score >= 75.0:
        signal = "STRONG BUY"
    elif score >= 60.0:
        signal = "BUY"
    elif score <= 25.0:
        signal = "STRONG SELL"
    elif score <= 40.0:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "score": round(score, 2),
        "conviction": round(conviction, 4),
        "forecast_return": round(forecast_return, 6),
        "components": {
            "forecast_return": round(forecast_signal, 4),
            "trend": round(trend_signal, 4),
            "model_consensus": round(model_consensus, 4),
            "validation": round(validation_strength, 4),
            "news_sentiment": round(sentiment_signal, 4),
            "source_agreement": round(_clip(2.0 * float(source_agreement) - 1.0, -1.0, 1.0), 4),
            "data_quality": round(_clip(2.0 * float(data_quality) - 1.0, -1.0, 1.0), 4),
        },
        "weights": {
            "forecast_return": 0.30,
            "trend": 0.20,
            "model_consensus": 0.20,
            "validation": 0.15,
            "news_sentiment": 0.10,
            "source_agreement": 0.05,
            "data_quality": 0.05,
        },
        "volatility_penalty": round(volatility_penalty, 4),
        "research_only": True,
    }
