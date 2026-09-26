import numpy as np
import pandas as pd

def attach_research_features(price_df:pd.DataFrame,fundamentals:dict|None=None,news:dict|None=None)->pd.DataFrame:
    out=price_df.copy()
    f=fundamentals or {}
    n=news or {}
    # Research snapshots are treated as information available from the snapshot timestamp.
    # Callers should supply only observations whose published/filing timestamps precede the forecast origin.
    for key in ["revenue_growth","eps_growth","profit_margin","roe","operating_margin","quarterly_revenue_growth",
                "pe_ratio","peg_ratio","debt_to_equity"]:
        value=f.get(key)
        out["fund_"+key]=float(value) if value is not None else np.nan
    out["fund_coverage"]=float(f.get("coverage",0))
    out["news_sentiment"]=float(n.get("mean_sentiment",0))
    out["news_articles"]=float(n.get("articles",0))
    out["news_positive_ratio"]=float(n.get("positive_articles",0))/max(out["news_articles"].iloc[-1],1.0)
    out["news_negative_ratio"]=float(n.get("negative_articles",0))/max(out["news_articles"].iloc[-1],1.0)
    return out

def model_feature_columns():
    return [
        "return_1d","return_5d","return_20d","rsi_14","macd","macd_signal",
        "volatility_20d","volume_ratio_20d","trend_score",
        "fund_revenue_growth","fund_eps_growth","fund_profit_margin","fund_roe",
        "fund_operating_margin","fund_quarterly_revenue_growth","fund_pe_ratio",
        "fund_peg_ratio","fund_debt_to_equity","fund_coverage",
        "news_sentiment","news_articles","news_positive_ratio","news_negative_ratio"
    ]
