from backend.analytics.decision import decision_snapshot


def test_strong_buy_requires_aligned_positive_signals():
    result = decision_snapshot(
        last_price=100,
        forecast_price=108,
        trend_score=0.9,
        directional_accuracy=0.75,
        data_quality=0.95,
        news_sentiment=0.30,
        ml_prices=[107, 109],
        volatility=0.15,
    )
    assert result["signal"] == "STRONG BUY"
    assert result["score"] >= 75
    assert result["conviction"] > 0.5


def test_strong_sell_for_aligned_negative_signals():
    result = decision_snapshot(
        last_price=100,
        forecast_price=92,
        trend_score=0.1,
        directional_accuracy=0.25,
        data_quality=0.95,
        news_sentiment=-0.30,
        ml_prices=[91, 93],
        volatility=0.15,
    )
    assert result["signal"] == "STRONG SELL"
    assert result["score"] <= 25


def test_high_volatility_reduces_conviction():
    calm = decision_snapshot(
        last_price=100,
        forecast_price=105,
        trend_score=0.8,
        directional_accuracy=0.70,
        data_quality=1.0,
        news_sentiment=0.20,
        ml_prices=[104, 106],
        volatility=0.10,
    )
    volatile = decision_snapshot(
        last_price=100,
        forecast_price=105,
        trend_score=0.8,
        directional_accuracy=0.70,
        data_quality=1.0,
        news_sentiment=0.20,
        ml_prices=[104, 106],
        volatility=0.90,
    )
    assert volatile["conviction"] < calm["conviction"]


def test_research_levels_use_atr_and_signal_direction():
    from backend.analytics.trade_levels import research_levels

    buy = research_levels(last_price=100, forecast_price=112, atr_14=4, signal="STRONG BUY")
    sell = research_levels(last_price=100, forecast_price=88, atr_14=4, signal="STRONG SELL")
    hold = research_levels(last_price=100, forecast_price=101, atr_14=4, signal="HOLD")

    assert buy["direction"] == "long"
    assert buy["entry_zone"]["low"] < 100 < buy["entry_zone"]["high"]
    assert buy["invalidation"] < 100
    assert buy["target"] == 112
    assert buy["risk_reward"] > 0

    assert sell["direction"] == "short"
    assert sell["invalidation"] > 100
    assert sell["target"] == 88

    assert hold["direction"] == "neutral"
    assert hold["invalidation"] is None
