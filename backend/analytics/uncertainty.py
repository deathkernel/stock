import numpy as np

def conformal_interval(actual,predicted,point,alpha=.1):
    a=np.asarray(actual,dtype=float); p=np.asarray(predicted,dtype=float)
    if len(a)==0 or len(a)!=len(p):
        raise ValueError("Calibration arrays must be non-empty and equal length")
    residuals=np.abs(a-p)
    q=float(np.quantile(residuals,min(1.0,max(0.0,1-alpha)),method="higher"))
    return {"point":float(point),"lower":float(point-q),"upper":float(point+q),"alpha":float(alpha),"calibration_size":len(a),"residual_quantile":q}

def conformal_relative_interval(actual,predicted,point,alpha=.1):
    a=np.asarray(actual,dtype=float); p=np.asarray(predicted,dtype=float)
    scale=np.maximum(np.abs(a),1e-9)
    scores=np.abs(a-p)/scale
    q=float(np.quantile(scores,min(1.0,max(0.0,1-alpha)),method="higher"))
    return {"point":float(point),"lower":float(point*(1-q)),"upper":float(point*(1+q)),"alpha":float(alpha),"relative_error_quantile":q}
