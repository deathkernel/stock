from dataclasses import dataclass
import numpy as np
import pandas as pd
def _sklearn_components():
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        return HistGradientBoostingRegressor, RandomForestRegressor, mean_absolute_error, mean_squared_error
    except Exception as exc:
        raise RuntimeError(
            "scikit-learn is unavailable in this Python environment. "
            "The installed native sklearn DLL may be blocked by Windows Application Control."
        ) from exc

FEATURES=["return_1d","return_5d","return_20d","rsi_14","macd","macd_signal","volatility_20d","volume_ratio_20d","trend_score"]

@dataclass
class MLForecast:
    point:float
    mae:float
    rmse:float
    direction_accuracy:float
    return_correlation:float
    model:str

def _evaluate(model,train,test):
    _, _, mean_absolute_error, mean_squared_error = _sklearn_components()
    model.fit(train[FEATURES],train["target"]); pred=model.predict(test[FEATURES])
    mae=float(mean_absolute_error(test["target"],pred)); rmse=float(np.sqrt(mean_squared_error(test["target"],pred)))
    base=test["close"].to_numpy(); actual=test["target"].to_numpy()
    direction=float(np.mean(np.sign(actual-base)==np.sign(pred-base)))
    ar=actual/base-1; pr=pred/base-1
    corr=float(np.corrcoef(ar,pr)[0,1]) if len(ar)>1 and np.std(ar)>0 and np.std(pr)>0 else 0.0
    return mae,rmse,direction,corr

def train_gradient_forecast(df:pd.DataFrame,horizon:int=5)->MLForecast:
    HistGradientBoostingRegressor, RandomForestRegressor, _, _ = _sklearn_components()
    data=df.copy(); data["target"]=data["close"].shift(-horizon)
    data=data.dropna(subset=FEATURES+["target"])
    if len(data)<120: raise ValueError("At least 120 feature rows are required for ML forecasting")
    split=max(int(len(data)*.8),100); train,test=data.iloc[:split],data.iloc[split:]
    if test.empty: raise ValueError("Not enough out-of-sample rows")
    candidates=[
        ("hist_gradient_boosting",HistGradientBoostingRegressor(max_iter=300,learning_rate=.04,max_leaf_nodes=15,l2_regularization=.1,random_state=42)),
        ("random_forest",RandomForestRegressor(n_estimators=300,max_depth=8,min_samples_leaf=3,max_features=.8,n_jobs=-1,random_state=42))
    ]
    results=[]
    for name,model in candidates:
        mae,rmse,direction,corr=_evaluate(model,train,test)
        results.append((name,model,mae,rmse,direction,corr))
    results.sort(key=lambda x:(x[2],-x[4],-x[5]))
    name,model,mae,rmse,direction,corr=results[0]
    model.fit(data[FEATURES],data["target"])
    latest=float(model.predict(data.iloc[[-1]][FEATURES])[0])
    return MLForecast(latest,mae,rmse,direction,corr,name)
