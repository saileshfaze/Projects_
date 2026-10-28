"""Offline single-change detection by minimizing within-segment squared error."""

def best_split(values: list[float], min_segment: int=8) -> dict | None:
    n=len(values)
    if min_segment<2: raise ValueError("min_segment must be >=2")
    if n<2*min_segment: return None
    total=sum(values); squares=sum(x*x for x in values)
    base=max(0.,squares-total*total/n)
    left_sum=left_sq=0.; best=None
    for j,x in enumerate(values,1):
        left_sum+=x; left_sq+=x*x
        if j<min_segment or j>n-min_segment: continue
        right_sum=total-left_sum; right_sq=squares-left_sq
        loss=max(0.,left_sq-left_sum**2/j)+max(0.,right_sq-right_sum**2/(n-j))
        gain=max(0.,base-loss)
        if best is None or gain>best["gain"]:
            best={"index":j,"gain":gain,"before_mean":left_sum/j,"after_mean":right_sum/(n-j),"relative_gain":gain/base if base>0 else 0.}
    return best
