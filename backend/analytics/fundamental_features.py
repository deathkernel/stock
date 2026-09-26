import math

FIELDS={
    "QuarterlyRevenueGrowthYOY":"revenue_growth",
    "EPSGrowthTTMYoy":"eps_growth",
    "ProfitMargin":"profit_margin",
    "ReturnOnEquityTTM":"roe",
    "OperatingMarginTTM":"operating_margin",
    
}

def _num(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError):
        return None

def extract_fundamental_features(overview:dict)->dict:
    data=overview.get("data",overview)
    out={}
    for source,target in FIELDS.items():
        value=_num(data.get(source))
        if value is not None: out[target]=value
    for source,target in [("PERatio","pe_ratio"),("PEGRatio","peg_ratio"),("DebtToEquity","debt_to_equity"),
                          ("BookValue","book_value"),("DividendYield","dividend_yield")]:
        value=_num(data.get(source))
        if value is not None: out[target]=value
    return out

def fundamental_signal(features:dict)->dict:
    positive=[]
    negative=[]
    for k in ("revenue_growth","eps_growth","profit_margin","roe","operating_margin","quarterly_revenue_growth"):
        if features.get(k) is not None:
            (positive if features[k]>0 else negative).append(k)
    return {"coverage":len(features),"positive_count":len(positive),"negative_count":len(negative),
            "positive_factors":positive,"negative_factors":negative}
