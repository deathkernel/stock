from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

FEATURES=["return_1d","return_5d","return_20d","rsi_14","macd","macd_signal","volatility_20d","volume_ratio_20d","trend_score"]

@dataclass
class MLForecast:
    point: float
    mae: float
    rmse: float
    direction_accuracy: float
    model: str

def train_gradient_forecast(df:pd.DataFrame,horizon:int=5)->MLForecast:
    data=df.copy()
    data["target"]=data["close"].shift(-horizon)
    data=data.dropna(subset=FEATURES+["target"])
    if len(data)<100: raise ValueError("At least 100 feature rows are required for ML forecasting")
    split=max(int(len(data)*.8),1)
    train,test=data.iloc[:split],data.iloc[split:]
    if test.empty: raise ValueError("Not enough out-of-sample rows")
    model=HistGradientBoostingRegressor(max_iter=250,learning_rate=.05,max_leaf_nodes=15,random_state=42)
    model.fit(train[FEATURES],train["target"])
    pred=model.predict(test[FEATURES])
    mae=float(mean_absolute_error(test["target"],pred)); rmse=float(np.sqrt(mean_squared_error(test["target"],pred)))
    base=test["close"].to_numpy()
    direction=float(np.mean(np.sign(test["target"].to_numpy()-base)==np.sign(pred-base)))
    latest=model.predict(data.iloc[[-1]][FEATURES])[0]
    return MLForecast(float(latest),mae,rmse,direction,"hist_gradient_boosting")
