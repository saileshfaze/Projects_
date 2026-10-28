"""Two-sided standardized cumulative-sum chart for sustained mean shifts."""
from .models import Baseline
from .rules import Signal

def cusum(values: list[float], ref: Baseline, k: float=0.5, h: float=5.0, reset: bool=True) -> tuple[list[tuple[float,float]],list[Signal]]:
    if k<=0 or h<=0: raise ValueError("k and h must be positive")
    plus=minus=0.0; trace=[]; alarms=[]
    for i,x in enumerate(values):
        zi=(x-ref.center)/ref.sigma
        plus=max(0.0,plus+zi-k)
        minus=max(0.0,minus-zi-k)
        trace.append((plus,minus))
        if plus>h or minus>h:
            direction="up" if plus>h else "down"
            alarms.append(Signal(i,"cusum_"+direction,"warning",x,f"CUSUM {direction} threshold exceeded"))
            if reset: plus=minus=0.0
    return trace,alarms
