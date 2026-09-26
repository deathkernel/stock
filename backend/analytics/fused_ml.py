from dataclasses import dataclass
import numpy as np
import pandas as pd
def _sklearn_components():
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.pipeline import make_pipeline
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        return HistGradientBoostingRegressor, SimpleImputer, make_pipeline, mean_absolute_error, mean_squared_error
    except Exception as exc:
        raise RuntimeError(
            "scikit-learn is unavailable in this Python environment. "
            "The installed native sklearn DLL may be blocked by Windows Application Control."
        ) from exc
from backend.analytics.fusion_features import model_feature_columns

@dataclass
class FusedForecast:
    point:float
    mae:float
    rmse:float
    directional_accuracy:float
    return_correlation:float
    model:str
    feature_count:int

def train_fused_forecast(df:pd.DataFrame,horizon:int=5)->FusedForecast:
    HistGradientBoostingRegressor, SimpleImputer, make_pipeline, mean_absolute_error, mean_squared_error = _sklearn_components()
    cols=[c for c in model_feature_columns() if c in df.columns]
    data=df.copy()
    data["target"]=data["close"].shift(-horizon)
    data=data.dropna(subset=["target"])
    if len(data)<140 or len(cols)<12:
        raise ValueError("Insufficient fused research history/features")
    split=int(len(data)*.8)
    train,test=data.iloc[:split],data.iloc[split:]
    model=make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingRegressor(max_iter=350,learning_rate=.035,max_leaf_nodes=15,
                                      l2_regularization=.2,random_state=42)
    )
    model.fit(train[cols],train["target"])
    pred=model.predict(test[cols])
    actual=test["target"].to_numpy(); base=test["close"].to_numpy()
    mae=float(mean_absolute_error(actual,pred))
    rmse=float(np.sqrt(mean_squared_error(actual,pred)))
    direction=float(np.mean(np.sign(actual-base)==np.sign(pred-base)))
    ar=actual/base-1; pr=pred/base-1
    corr=float(np.corrcoef(ar,pr)[0,1]) if len(ar)>1 and np.std(ar)>0 and np.std(pr)>0 else 0.0
    model.fit(data[cols],data["target"])
    latest=float(model.predict(data.iloc[[-1]][cols])[0])
    return FusedForecast(latest,mae,rmse,direction,corr,"fused_hist_gradient_boosting",len(cols))
