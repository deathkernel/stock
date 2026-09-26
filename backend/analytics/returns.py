import numpy as np
import pandas as pd

def add_return_targets(df:pd.DataFrame,horizons=(1,5,10,20)):
    out=df.copy()
    for h in horizons:
        out[f"target_return_{h}d"]=out["close"].shift(-h)/out["close"]-1
    out["log_return"]=np.log(out["close"]).diff()
    return out
