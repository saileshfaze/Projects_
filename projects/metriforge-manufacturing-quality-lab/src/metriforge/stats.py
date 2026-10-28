"""Distribution-free descriptive utilities with explicit finite-sample assumptions."""
from math import sqrt
from statistics import mean, median, stdev
from .models import Baseline, QualitySpec

def baseline(values: list[float], *, robust: bool = True) -> Baseline:
    if len(values) < 8:
        raise ValueError("baseline requires at least 8 observations")
    if robust:
        center = median(values)
        mad = median([abs(x-center) for x in values])
        sigma = 1.4826 * mad
        method = "median_mad"
        if sigma < 1e-10:
            sigma = stdev(values)
            method = "median_sd_fallback"
    else:
        center, sigma, method = mean(values), stdev(values), "mean_sd"
    if sigma < 1e-10:
        raise ValueError("constant baseline has no estimable variation")
    return Baseline(center, sigma, len(values), method)

def capability(values: list[float], spec: QualitySpec) -> dict:
    """Cp/Cpk use moving-range sigma; Pp/Ppk use overall sample sigma.

    Both estimates assume a stable, approximately normal process. Returns nulls
    if there is insufficient data or zero variance, rather than fabricating precision.
    """
    n=len(values)
    if n < 20:
        return {"n": n, "cp": None, "cpk": None, "pp": None, "ppk": None, "mean": mean(values) if values else None, "note": "at least 20 readings required"}
    avg=mean(values)
    overall=stdev(values)
    moving=sum(abs(b-a) for a,b in zip(values,values[1:]))/(n-1)
    within=moving/1.128
    def indices(sigma):
        if sigma < 1e-12: return (None,None)
        return ((spec.usl-spec.lsl)/(6*sigma), min(spec.usl-avg, avg-spec.lsl)/(3*sigma))
    cp,cpk=indices(within); pp,ppk=indices(overall)
    return {"n":n,"cp":cp,"cpk":cpk,"pp":pp,"ppk":ppk,"mean":avg,"within_sigma":within,"overall_sigma":overall,"note":"normality and statistical stability not established"}

def defect_rate(values: list[float], spec: QualitySpec) -> float:
    if not values: raise ValueError("empty readings")
    return sum(not(spec.lsl <= x <= spec.usl) for x in values)/len(values)

def pearson(a: list[float], b: list[float]) -> float | None:
    if len(a) != len(b) or len(a) < 3: return None
    am,bm=mean(a),mean(b)
    num=sum((x-am)*(y-bm) for x,y in zip(a,b))
    da=sqrt(sum((x-am)**2 for x in a)); db=sqrt(sum((y-bm)**2 for y in b))
    return num/(da*db) if da>0 and db>0 else None
