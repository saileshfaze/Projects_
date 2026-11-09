"""Aggregate experiment outcomes using simple descriptive statistics."""
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Summary:
    variation: str
    exposures: int
    conversions: int
    rate: float
    wilson_low: float
    wilson_high: float

def summarize(events: list[dict], z: float = 1.96) -> list[Summary]:
    seen: dict[tuple[str,str], bool] = {}
    for event in events:
        key = (str(event['subject']), str(event['variation']))
        seen[key] = seen.get(key, False) or bool(event.get('converted', False))
    groups: dict[str, list[bool]] = {}
    for (_, variation), converted in seen.items():
        groups.setdefault(variation, []).append(converted)
    result = []
    for variation, values in sorted(groups.items()):
        n = len(values); k = sum(values); p = k / n
        center = (p + z*z/(2*n))/(1+z*z/n)
        half = z*sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
        result.append(Summary(variation,n,k,p,max(0,center-half),min(1,center+half)))
    return result
