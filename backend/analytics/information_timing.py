import pandas as pd

def asof_join_price_research(price_df:pd.DataFrame,research_df:pd.DataFrame,
                             research_time_col="published_at")->pd.DataFrame:
    if research_df is None or research_df.empty:
        return price_df.copy()
    left=price_df.copy()
    right=research_df.copy()
    left["date"]=pd.to_datetime(left["date"],utc=True)
    right[research_time_col]=pd.to_datetime(right[research_time_col],utc=True)
    right=right.sort_values(research_time_col)
    left=left.sort_values("date")
    # merge_asof guarantees that a price row only receives information published
    # on or before that timestamp.
    return pd.merge_asof(left,right,left_on="date",right_on=research_time_col,direction="backward")
