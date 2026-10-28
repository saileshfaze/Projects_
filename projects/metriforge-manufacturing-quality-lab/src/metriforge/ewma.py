"""Exponentially weighted moving average with time-dependent limits."""
from math import sqrt
from .models import Baseline
from .rules import Signal

def ewma(values: list[float], ref: Baseline, lam: float = 0.2, width: float = 3.0) -> tuple[list[float],list[Signal]]:
    if not 0 < lam <= 1 or width <= 0: raise ValueError("invalid EWMA parameters")
    z=ref.center; trace=[]; alarms=[]
    for i,x in enumerate(values):
        z=lam*x+(1-lam)*z
        trace.append(z)
        sigma_z=ref.sigma*sqrt(lam/(2-lam)*(1-(1-lam)**(2*(i+1))))
        if abs(z-ref.center)>width*sigma_z:
            alarms.append(Signal(i,"ewma","warning",x,f"EWMA {z:.4f} outside dynamic limit"))
    return trace,alarms
