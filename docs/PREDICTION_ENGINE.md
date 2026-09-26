# Prediction Engine

Forecasting is treated as a validation problem, not a single-model guess.

## Current pipeline

1. Normalize multi-provider OHLCV data.
2. Build lagged technical and return features.
3. Run exponential smoothing and autoregressive return models.
4. Run ML candidates including gradient boosting and random forest.
5. Evaluate chronologically so future observations never enter training.
6. Compare against a naive last-price baseline.
7. Weight statistical ensemble members from rolling out-of-sample error.
8. Detect market regime from trend, volatility and recent return.
9. Calibrate forecast uncertainty from rolling out-of-sample residuals.
10. Expose MAE, RMSE, directional accuracy, return correlation and baseline improvement.

## Uncertainty

Conformal-style relative residual calibration provides a distribution-free uncertainty utility. Coverage is measured from historical out-of-sample predictions and should be monitored separately by horizon and regime.

## Model selection

The leaderboard combines error, directional accuracy and return correlation. These are validation measurements, not guarantees of future performance.

## Remaining prediction milestones

- Integrate calibrated intervals into the primary research response.
- Add XGBoost/LightGBM after dependency review.
- Add regime-specific model validation.
- Add time-series hyperparameter optimization.
- Add fundamentals/news/event features.
- Add portfolio-level forecasting and stress testing.
