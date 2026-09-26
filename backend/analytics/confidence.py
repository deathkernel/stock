def confidence_score(*,data_quality:float,model_agreement:float,backtest_directional_accuracy:float,horizon:int)->dict:
    penalty=min(max(horizon-1,0)/100,.25)
    score=max(0,min(1,.35*data_quality+.35*model_agreement+.30*backtest_directional_accuracy-penalty))
    return {"score":score,"label":"high" if score>=.75 else "moderate" if score>=.55 else "low",
            "drivers":{"data_quality":data_quality,"model_agreement":model_agreement,
            "backtest_directional_accuracy":backtest_directional_accuracy,"horizon_penalty":penalty}}
