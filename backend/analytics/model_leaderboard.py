from dataclasses import dataclass,asdict
import numpy as np

@dataclass
class ModelScore:
    model:str
    mae:float
    rmse:float
    directional_accuracy:float
    return_correlation:float
    score:float

def score_models(results:list[dict])->list[dict]:
    valid=[]
    for r in results:
        if not np.isfinite(r.get("mae",np.nan)): continue
        mae=max(float(r["mae"]),1e-9)
        direction=float(r.get("directional_accuracy",0))
        corr=float(r.get("return_correlation",0))
        rmse=float(r.get("rmse",mae))
        # Scale-aware normalized score: lower error + stronger directional/correlation signal.
        score=(1/(1+mae))*.45+(1/(1+rmse))*.20+direction*.25+max(-1,min(1,corr))*.10
        valid.append(ModelScore(str(r["model"]),mae,rmse,direction,corr,float(score)))
    return [asdict(x) for x in sorted(valid,key=lambda x:x.score,reverse=True)]
