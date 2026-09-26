# Stock Intelligence Roadmap

## Data
- [x] Provider abstraction
- [x] Alpha Vantage historical connector
- [x] Twelve Data historical connector
- [x] Finnhub historical connector
- [x] SEC EDGAR company facts connector
- [x] OHLCV normalization
- [x] Data quality report
- [x] Provider fallback/orchestration
- [ ] Persistent cache
- [ ] PostgreSQL models
- [x] News ingestion
- [x] Fundamentals ingestion
- [ ] Earnings/analyst ingestion
- [ ] Macro/sector ingestion

## Analytics
- [x] RSI, EMA, SMA, MACD, Bollinger, ATR
- [x] Returns and volatility
- [x] Trend score
- [x] Risk metrics
- [x] Exponential forecasting baseline
- [x] Ensemble contract
- [x] Walk-forward backtesting
- [ ] XGBoost/LightGBM model
- [ ] LSTM/GRU model
- [x] Regime detection
- [x] Probability calibration
- [ ] Feature importance
- [ ] Model registry/versioning

## Decision support
- [x] Explainable decision contract
- [x] Scenario analysis
- [x] Confidence decomposition
- [ ] Data-source agreement
- [ ] Risk-adjusted forecast
- [x] Portfolio-level analysis

## Product
- [x] FastAPI skeleton
- [x] React/Vite skeleton
- [x] Interactive charts
- [x] Stock search
- [x] Analysis report
- [ ] News timeline
- [x] Backtest dashboard
- [ ] AI analyst
- [ ] Authentication


## Visual analytics milestone
- Historical close chart with forecast estimate and uncertainty band
- Compact evidence and risk panels
- Portfolio risk-contribution visualization
- Dashboard history endpoint returns chart-ready normalized close data


## Final engineering audit
- [x] Expanded analytics, API, research-pipeline, data-quality, risk-edge, and portfolio test coverage
- [x] GitHub Actions CI with dependency installation, compile check, and pytest
- [x] SEC client uses configured user-agent settings
- [x] Fundamental revenue-growth mapping corrected to a growth field
- [x] ATR corrected to use true range rather than simple high-low range
- [x] Frontend chart and portfolio visualization integrated
\n\n## Production hardening v2\n- [x] Request IDs and response timing\n- [x] Structured request logging\n- [x] Lightweight application metrics endpoint\n- [x] Bounded TTL research cache\n- [x] Concurrent request de-duplication\n- [ ] Shared distributed cache for multi-instance deployments\n- [ ] Full Prometheus/OpenTelemetry integration\n\n\n## Deployment/runtime hardening\n- [x] Database connectivity readiness check\n- [x] Production frontend Docker image\n- [x] Nginx SPA routing\n- [x] Full API + frontend Docker Compose stack\n- [x] Container healthchecks and graceful shutdown\n- [x] Docker build exclusions\n- [x] Frontend production build in CI\n- [ ] External reverse proxy/TLS configuration\n- [ ] PostgreSQL migration and schema migrations\n