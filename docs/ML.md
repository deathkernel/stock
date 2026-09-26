# ML Layer

The first supervised model is HistGradientBoostingRegressor. It uses only lagged/derived market features and a chronological 80/20 split.

Metrics:
- MAE
- RMSE
- Directional accuracy

The statistical baseline and ML models are intended to be compared before an ensemble weight is chosen. No random train/test shuffle is used for time-series evaluation.
