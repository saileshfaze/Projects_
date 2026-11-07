"""Streaming-friendly short/long average energy detector; not an operational alarm."""
from math import isfinite
from .models import Pick

def characteristic(samples, short=10, long=100):
    if not (isinstance(short,int) and isinstance(long,int) and 0 < short < long):
        raise ValueError("expected 0 < short < long")
    values = list(samples)
    if any(not isfinite(v) for v in values):
        raise ValueError("nonfinite samples")
    energy = [abs(v) for v in values]
    prefix = [0.0]
    for e in energy:
        prefix.append(prefix[-1] + e)
    ratios = [0.0] * len(values)
    for i in range(long-1,len(values)):
        s=(prefix[i+1]-prefix[i+1-short])/short
        l=(prefix[i+1]-prefix[i+1-long])/long
        ratios[i]=s/l if l>1e-12 else 0.0
    return ratios

def detect(samples, station, sample_hz, threshold=2.8, short=10, long=100, cooldown_s=0.8):
    if sample_hz<=0 or threshold<=1 or cooldown_s<0:
        raise ValueError("invalid detection parameters")
    ratios=characteristic(samples,short,long)
    out=[]
    armed=True
    last=-float('inf')
    for i,r in enumerate(ratios):
        t=i/sample_hz
        if r>=threshold and armed and t-last>=cooldown_s:
            out.append(Pick(station,t,r));last=t;armed=False
        elif r<threshold*0.65:
            armed=True
    return out
