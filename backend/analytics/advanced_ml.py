from dataclasses import dataclass
import numpy as np
import pandas as pd
def _sklearn_components():
    try:
        from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        return ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor, mean_absolute_error, mean_squared_error
    except Exception as exc:
        raise RuntimeError(
            "scikit-learn is unavailable in this Python environment. "
            "The installed native sklearn DLL may be blocked by Windows Application Control."
        ) from exc

FEATURES=[
    "return_1d","return_5d","return_20d","rsi_14","macd","macd_signal",
    "volatility_20d","volume_ratio_20d","trend_score"
]

@dataclass
class CandidateResult:
    model:str
    mae:float
    rmse:float
    directional_accuracy:float
    return_correlation:float
    prediction:float

def _evaluate(model,train,test):
    _, _, _, mean_absolute_error, mean_squared_error = _sklearn_components()
    model.fit(train[FEATURES],train["target"])
    pred=model.predict(test[FEATURES])
    actual=test["target"].to_numpy(); base=test["close"].to_numpy()
    mae=float(mean_absolute_error(actual,pred))
    rmse=float(np.sqrt(mean_squared_error(actual,pred)))
    direction=float(np.mean(np.sign(actual-base)==np.sign(pred-base)))
    ar=actual/base-1; pr=pred/base-1
    corr=float(np.corrcoef(ar,pr)[0,1]) if len(ar)>1 and np.std(ar)>0 and np.std(pr)>0 else 0.0
    return mae,rmse,direction,corr,pred

def evaluate_candidates(df:pd.DataFrame,horizon:int=5)->list[dict]:
    ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor, _, _ = _sklearn_components()
    data=df.copy()
    data["target"]=data["close"].shift(-horizon)
    data=data.dropna(subset=FEATURES+["target"]).reset_index(drop=True)
    if len(data)<140:
        raise ValueError("At least 140 observations are required for advanced ML")
    split=int(len(data)*.8)
    train,test=data.iloc[:split],data.iloc[split:]
    candidates=[
        ("hist_gradient_boosting",HistGradientBoostingRegressor(max_iter=300,learning_rate=.04,max_leaf_nodes=15,l2_regularization=.1,random_state=42)),
        ("random_forest",RandomForestRegressor(n_estimators=300,max_depth=8,min_samples_leaf=3,max_features=.8,n_jobs=-1,random_state=42)),
        ("extra_trees",ExtraTreesRegressor(n_estimators=300,max_depth=10,min_samples_leaf=3,max_features=.8,n_jobs=-1,random_state=42)),
    ]
    results=[]
    for name,model in candidates:
        mae,rmse,direction,corr,pred=_evaluate(model,train,test)
        model.fit(data[FEATURES],data["target"])
        latest=float(model.predict(data.iloc[[-1]][FEATURES])[0])
        results.append(CandidateResult(name,mae,rmse,direction,corr,latest))
    return [r.__dict__ for r in sorted(results,key=lambda r:(r["mae"],-r["directional_accuracy"],-r["return_correlation"]))]

def time_series_search(df:pd.DataFrame,horizon:int=5)->dict:
    _, _, HistGradientBoostingRegressor, _, _ = _sklearn_components()
    data=df.copy()
    data["target"]=data["close"].shift(-horizon)
    data=data.dropna(subset=FEATURES+["target"]).reset_index(drop=True)
    if len(data)<180: raise ValueError("At least 180 observations are required for time-series search")
    configs=[
        {"max_iter":200,"learning_rate":.08,"max_leaf_nodes":7,"l2_regularization":.1},
        {"max_iter":300,"learning_rate":.04,"max_leaf_nodes":15,"l2_regularization":.1},
        {"max_iter":400,"learning_rate":.025,"max_leaf_nodes":31,"l2_regularization":.5},
    ]
    folds=[]
    for cfg in configs:
        scores=[]
        for end in [int(len(data)*.55),int(len(data)*.70),int(len(data)*.85)]:
            if end+horizon>len(data): continue
            train=data.iloc[:end]; test=data.iloc[end:min(end+max(10,horizon*2),len(data))]
            model=HistGradientBoostingRegressor(random_state=42,**cfg)
            mae,rmse,direction,corr,_=_evaluate(model,train,test)
            scores.append({"mae":mae,"rmse":rmse,"directional_accuracy":direction,"return_correlation":corr})
        if scores:
            folds.append({"config":cfg,"mae":float(np.mean([x["mae"] for x in scores])),"rmse":float(np.mean([x["rmse"] for x in scores])),
                          "directional_accuracy":float(np.mean([x["directional_accuracy"] for x in scores])),
                          "return_correlation":float(np.mean([x["return_correlation"] for x in scores]))})
    folds.sort(key=lambda x:(x["mae"],-x["directional_accuracy"]))
    return {"folds":folds,"selected_config":folds[0]["config"] if folds else None}


def feature_importance(df:pd.DataFrame,horizon:int=5)->dict:
    ExtraTreesRegressor, _, _, _, _ = _sklearn_components()
    from sklearn.inspection import permutation_importance

    data=df.copy()
    data["target"]=data["close"].shift(-horizon)
    data=data.dropna(subset=FEATURES+["target"]).reset_index(drop=True)
    if len(data)<140:
        raise ValueError("At least 140 observations are required for feature importance")

    split=int(len(data)*0.8)
    train,test=data.iloc[:split],data.iloc[split:]
    model=ExtraTreesRegressor(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=3,
        max_features=.8,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(train[FEATURES],train["target"])
    result=permutation_importance(
        model,
        test[FEATURES],
        test["target"],
        n_repeats=8,
        random_state=42,
        scoring="neg_mean_absolute_error",
    )
    rows=[
        {"feature":feature,"importance":float(max(0.0,score))}
        for feature,score in zip(FEATURES,result.importances_mean)
    ]
    rows.sort(key=lambda x:x["importance"],reverse=True)
    total=sum(x["importance"] for x in rows)
    for row in rows:
        row["relative_importance"]=float(row["importance"]/total) if total else 0.0
    return {
        "model":"extra_trees",
        "method":"permutation_importance",
        "observations":len(test),
        "features":rows,
    }
