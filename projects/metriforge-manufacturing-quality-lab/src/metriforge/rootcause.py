"""Rank aligned process covariates by correlation with deviations; not causal attribution."""
from .stats import pearson

def rank_covariates(deviation: list[float], covariates: dict[str,list[float]]) -> list[dict]:
    out=[]
    for name,series in covariates.items():
        corr=pearson(deviation,series)
        if corr is not None: out.append({"name":name,"correlation":corr,"abs_correlation":abs(corr)})
    return sorted(out,key=lambda row:(-row["abs_correlation"],row["name"]))
