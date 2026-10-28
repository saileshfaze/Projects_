"""Regularized Mahalanobis distance for correlated measurement streams."""
import numpy as np

def multivariate_scores(reference: list[list[float]], observed: list[list[float]], ridge: float=0.05) -> dict:
    x=np.asarray(reference,dtype=float); y=np.asarray(observed,dtype=float)
    if x.ndim!=2 or y.ndim!=2 or x.shape[1]!=y.shape[1] or len(x)<max(8,x.shape[1]+2):
        raise ValueError("incompatible matrices or insufficient baseline")
    if not np.isfinite(x).all() or not np.isfinite(y).all(): raise ValueError("non-finite features")
    if not 0<ridge<=1: raise ValueError("ridge must be in (0,1]")
    center=np.mean(x,axis=0)
    cov=np.atleast_2d(np.cov(x,rowvar=False))
    diag=np.diag(np.maximum(np.diag(cov),1e-8))
    shrink=(1-ridge)*cov+ridge*diag+np.eye(x.shape[1])*1e-8
    inv=np.linalg.pinv(shrink)
    residual=y-center
    distances=np.einsum('ij,jk,ik->i',residual,inv,residual)
    ref_res=x-center
    ref_scores=np.einsum('ij,jk,ik->i',ref_res,inv,ref_res)
    threshold=float(np.quantile(ref_scores,0.99))
    return {"scores":distances.tolist(),"threshold":threshold,"flagged_indices":[i for i,v in enumerate(distances) if v>threshold],"baseline_n":len(x),"features":x.shape[1],"note":"empirical in-sample threshold; exploratory only"}
