# Stock Intelligence Platform

AI-assisted stock analysis, forecasting, risk analytics, backtesting, and explainable decision support.

## Vision
Stock combines historical market data, fundamentals, technical indicators, news/sentiment, macro context, and multiple forecasting models into one research workflow.

**Important:** forecasts are probabilistic research outputs, not guaranteed returns or financial advice.

## Initial architecture
- Frontend: React + Vite (planned)
- Backend: FastAPI
- Data: PostgreSQL
- Analytics: pandas, NumPy, scikit-learn, statsmodels
- ML: XGBoost/LightGBM-compatible interface
- Optional deep learning: PyTorch
- Data providers: Alpha Vantage, Twelve Data, Finnhub, SEC EDGAR
- Backtesting: walk-forward validation

## Providers
Alpha Vantage offers broad market, fundamental, news/sentiment, economic and technical endpoints.
Twelve Data provides global time-series, technical indicators and fundamentals.
Finnhub provides market data, financial statements, estimates, technical analysis and news/sentiment.
SEC EDGAR provides official US filing/XBRL data without an API key.

Provider credentials are loaded from environment variables and never committed.

## Roadmap
1. Provider abstraction and normalized market schema
2. Historical ingestion and caching
3. Technical/fundamental feature engine
4. News and sentiment pipeline
5. Forecasting baselines and ML models
6. Walk-forward backtesting
7. Ensemble and confidence engine
8. Risk/scenario analysis
9. FastAPI endpoints
10. React research dashboard
11. Explainable AI analyst
12. Tests, documentation and deployment


## Portfolio intelligence
The platform now includes a portfolio research layer with:
- normalized multi-asset weights and overlapping return history
- correlation matrix and concentration metrics
- annualized return/volatility, Sharpe ratio, and maximum drawdown
- historical Value at Risk (VaR) and Conditional VaR (CVaR)
- benchmark beta when benchmark history is supplied
- per-position risk contribution estimates
- deterministic stress scenarios for market shocks and volatility shocks
- FastAPI endpoints for direct price-series analysis and symbol-based provider-backed analysis
- a simple dashboard portfolio risk lab

Portfolio outputs are historical/statistical risk measures and scenario estimates. They are not guaranteed loss limits or personalized financial advice.


## Interactive research dashboard
The dashboard now includes a historical price visualization, a forecast estimate marker with uncertainty range, validation evidence cards, risk/scenario cards, and a portfolio risk-contribution view. Historical chart data is limited to a recent window for responsive rendering.


## Quality checks
GitHub Actions runs Python 3.11 dependency installation, Python bytecode compilation, and the complete pytest suite on pushes and pull requests targeting `main`. The suite covers analytics, forecasting, ML, research feature fusion, data quality, portfolio risk, API contracts, and edge cases.
