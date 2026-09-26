from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class PortfolioAnalysis:
    observations: int
    annualized_return: float
    annualized_volatility: float
    sharpe: float
    max_drawdown: float
    var: float
    cvar: float
    var_method: str
    beta: float | None
    correlation_matrix: dict
    risk_contribution: dict
    concentration: dict
    stress_tests: list[dict]


def _clean_series(values) -> pd.Series:
    s = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
    if len(s) < 2:
        raise ValueError("Each asset needs at least two valid price observations")
    return s.reset_index(drop=True)


def _portfolio_returns(assets: list[dict]) -> tuple[pd.DataFrame, np.ndarray]:
    if not assets:
        raise ValueError("At least one asset is required")
    symbols, series, weights = [], [], []
    for asset in assets:
        symbol = str(asset.get("symbol", "")).upper().strip()
        if not symbol:
            raise ValueError("Each asset requires a symbol")
        weight = float(asset.get("weight", 0))
        if not np.isfinite(weight):
            raise ValueError(f"Invalid weight for {symbol}")
        prices = _clean_series(asset.get("close", []))
        symbols.append(symbol)
        series.append(prices.rename(symbol))
        weights.append(weight)
    weights = np.asarray(weights, dtype=float)
    if np.allclose(weights.sum(), 0):
        raise ValueError("Portfolio weights cannot sum to zero")
    weights = weights / weights.sum()
    prices = pd.concat(series, axis=1).dropna()
    if len(prices) < 2:
        raise ValueError("Assets do not have enough overlapping history")
    returns = prices.pct_change().dropna()
    return returns, weights


def _historical_var_cvar(returns: pd.Series, confidence: float) -> tuple[float, float]:
    alpha = 1 - confidence
    losses = -returns.to_numpy(dtype=float)
    var = float(np.quantile(losses, confidence))
    tail = losses[losses >= var]
    cvar = float(tail.mean()) if len(tail) else var
    return var, cvar


def _stress_tests(portfolio_returns: pd.Series) -> list[dict]:
    daily_vol = float(portfolio_returns.std())
    scenarios = [
        ("market_shock_-5pct", -0.05),
        ("market_shock_-10pct", -0.10),
        ("market_shock_-20pct", -0.20),
        ("volatility_2x", -2.0 * daily_vol),
        ("volatility_3x", -3.0 * daily_vol),
    ]
    return [{"scenario": name, "estimated_portfolio_return": float(shock)}
            for name, shock in scenarios]


def analyze_portfolio(
    assets: list[dict],
    benchmark_close=None,
    confidence: float = 0.95,
) -> dict:
    if not 0.5 < confidence < 1:
        raise ValueError("confidence must be between 0.5 and 1")
    returns, weights = _portfolio_returns(assets)
    portfolio = returns.to_numpy() @ weights
    p = pd.Series(portfolio, index=returns.index, name="portfolio")
    equity = (1 + p).cumprod()
    drawdown = equity / equity.cummax() - 1
    vol = float(p.std() * np.sqrt(252))
    ann_return = float(equity.iloc[-1] ** (252 / len(p)) - 1)
    sharpe = float(p.mean() / p.std() * np.sqrt(252)) if p.std() else 0.0
    var, cvar = _historical_var_cvar(p, confidence)

    beta = None
    if benchmark_close is not None:
        benchmark = _clean_series(benchmark_close).pct_change().dropna()
        n = min(len(p), len(benchmark))
        pr = p.iloc[-n:].to_numpy()
        br = benchmark.iloc[-n:].to_numpy()
        variance = float(np.var(br, ddof=1)) if n > 1 else 0.0
        beta = float(np.cov(pr, br, ddof=1)[0, 1] / variance) if variance > 0 else None

    corr = returns.corr().fillna(0.0).round(6).to_dict()
    component_var = np.abs(weights * (returns.std(ddof=1).to_numpy() + 1e-12))
    rc = component_var / component_var.sum() if component_var.sum() else np.zeros_like(component_var)
    symbols = list(returns.columns)
    weights_dict = {s: float(w) for s, w in zip(symbols, weights)}
    risk_dict = {s: float(v) for s, v in zip(symbols, rc)}
    concentration = {
        "largest_weight": float(np.max(np.abs(weights))),
        "herfindahl_index": float(np.sum(weights ** 2)),
        "effective_number_of_positions": float(1 / np.sum(weights ** 2)),
        "weights": weights_dict,
    }
    return {
        "observations": int(len(p)),
        "annualized_return": ann_return,
        "annualized_volatility": vol,
        "sharpe": sharpe,
        "max_drawdown": float(drawdown.min()),
        "var": var,
        "cvar": cvar,
        "var_method": "historical",
        "confidence": confidence,
        "beta": beta,
        "correlation_matrix": corr,
        "risk_contribution": risk_dict,
        "concentration": concentration,
        "stress_tests": _stress_tests(p),
    }
