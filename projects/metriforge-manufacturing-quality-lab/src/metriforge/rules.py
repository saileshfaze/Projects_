"""Auditable Western Electric-style signal rules for individual observations."""
from dataclasses import dataclass
from .models import Baseline

@dataclass(frozen=True)
class Signal:
    index: int
    rule: str
    severity: str
    observed: float
    explanation: str
    def as_dict(self):
        return {"index":self.index,"rule":self.rule,"severity":self.severity,"observed":self.observed,"explanation":self.explanation}

def shewhart(values: list[float], ref: Baseline) -> list[Signal]:
    z=[(x-ref.center)/ref.sigma for x in values]
    signals=[]
    for i,zi in enumerate(z):
        if abs(zi)>3:
            signals.append(Signal(i,"beyond_3sigma","critical",values[i],f"standardized distance {zi:.2f}"))
        if i>=2 and (sum(v>2 for v in z[i-2:i+1])>=2 or sum(v< -2 for v in z[i-2:i+1])>=2):
            signals.append(Signal(i,"two_of_three_2sigma","warning",values[i],"2 of 3 points beyond 2 sigma on one side"))
        if i>=4 and (sum(v>1 for v in z[i-4:i+1])>=4 or sum(v< -1 for v in z[i-4:i+1])>=4):
            signals.append(Signal(i,"four_of_five_1sigma","warning",values[i],"4 of 5 points beyond 1 sigma on one side"))
        if i>=7 and (all(v>0 for v in z[i-7:i+1]) or all(v<0 for v in z[i-7:i+1])):
            signals.append(Signal(i,"eight_same_side","warning",values[i],"8 consecutive points on one side"))
        if i>=5:
            tail=values[i-5:i+1]
            if all(a<b for a,b in zip(tail,tail[1:])) or all(a>b for a,b in zip(tail,tail[1:])):
                signals.append(Signal(i,"six_trending","warning",values[i],"6 consecutive monotonic observations"))
    return signals
