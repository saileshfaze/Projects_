"""Seeded scenario-level positional perturbations for sensitivity analysis."""
from collections import Counter
from dataclasses import dataclass,asdict
from random import Random
from math import cos,radians
from .models import Flight,Fix,Thresholds
from .detector import detect
from .geometry import R_EARTH_M,FT_M

@dataclass(frozen=True)
class RiskEstimate:
    samples:int
    seed:int
    horizontal_sigma_m:float
    vertical_sigma_ft:float
    pair_probabilities:dict[str,float]

    def to_dict(self):return asdict(self)

def sample_risk(flights:tuple[Flight,...],thresholds:Thresholds=Thresholds(),samples:int=100,seed:int=42,horizontal_sigma_m:float=120.,vertical_sigma_ft:float=100.)->RiskEstimate:
    if not 1<=samples<=5000:raise ValueError('samples must be in [1,5000]')
    if horizontal_sigma_m<0 or vertical_sigma_ft<0:raise ValueError('sigma must be nonnegative')
    rng=Random(seed); counts=Counter()
    for _ in range(samples):
        perturbed=[]
        for f in flights:
            dx=rng.gauss(0,horizontal_sigma_m);dy=rng.gauss(0,horizontal_sigma_m)
            dz=rng.gauss(0,vertical_sigma_ft)
            fixes=[]
            for p in f.fixes:
                lat=p.lat+dy/R_EARTH_M*180/3.141592653589793
                lon=p.lon+dx/(R_EARTH_M*max(0.1,cos(radians(p.lat))))*180/3.141592653589793
                fixes.append(Fix(p.t,lat,lon,p.alt_ft+dz))
            perturbed.append(Flight(f.callsign,tuple(fixes)))
        for key in set(f'{c.a}|{c.b}' for c in detect(tuple(perturbed),thresholds)):
            counts[key]+=1
    return RiskEstimate(samples,seed,horizontal_sigma_m,vertical_sigma_ft,{k:round(v/samples,4) for k,v in sorted(counts.items())})
