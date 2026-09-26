def score_fundamentals(metrics:dict)->dict:
    weights={"revenue_growth":.20,"eps_growth":.20,"profit_margin":.15,"roe":.15,"free_cash_flow":.15,"debt_health":.15}
    available=[(k,float(metrics[k])) for k in weights if metrics.get(k) is not None]
    if not available:return {"score":None,"coverage":0.0,"components":{}}
    components={k:max(0,min(1,v)) for k,v in available}; total=sum(weights[k] for k in components)
    return {"score":sum(components[k]*weights[k] for k in components)/total,"coverage":len(available)/len(weights),"components":components}
