"""ATR-based research levels derived from the quantitative signal.

These are mechanical research levels, not personalized trading instructions.
"""


def research_levels(
    *,
    last_price: float,
    forecast_price: float,
    atr_14: float,
    signal: str,
) -> dict:
    price = max(float(last_price), 1e-9)
    forecast = float(forecast_price)
    atr = max(abs(float(atr_14)), price * 0.005)

    risk_distance = atr * 1.5
    entry_half_width = atr * 0.25
    direction = "long" if "BUY" in signal else "short" if "SELL" in signal else "neutral"

    if direction == "long":
        entry_low = max(0.0, price - entry_half_width)
        entry_high = price + entry_half_width
        invalidation = max(0.0, price - risk_distance)
        target = forecast if forecast > price else price + 2.0 * risk_distance
        expected_reward = max(0.0, target - price)
    elif direction == "short":
        entry_low = max(0.0, price - entry_half_width)
        entry_high = price + entry_half_width
        invalidation = price + risk_distance
        target = forecast if forecast < price else max(0.0, price - 2.0 * risk_distance)
        expected_reward = max(0.0, price - target)
    else:
        entry_low = max(0.0, price - entry_half_width)
        entry_high = price + entry_half_width
        invalidation = None
        target = forecast
        expected_reward = 0.0

    risk = risk_distance
    risk_reward = expected_reward / risk if risk > 0 else 0.0

    return {
        "direction": direction,
        "entry_reference": price,
        "entry_zone": {"low": entry_low, "high": entry_high},
        "invalidation": invalidation,
        "target": target,
        "atr_14": atr,
        "risk_distance": risk,
        "expected_reward": expected_reward,
        "risk_reward": risk_reward,
        "target_return": (target / price - 1.0) if price else 0.0,
        "risk_pct": risk / price if price else 0.0,
        "method": "1.5x ATR invalidation; model forecast target with 2R fallback",
        "research_only": True,
    }
