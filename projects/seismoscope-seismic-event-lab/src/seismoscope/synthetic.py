"""Deterministic synthetic arrivals; no real seismic recordings or location data."""
from math import hypot, exp, sin, pi
from random import Random
from .models import Station

def network():
    return {s.code:s for s in (Station('STA_A',-12,-12),Station('STA_B',12,-12),Station('STA_C',12,12),Station('STA_D',-12,12),Station('STA_E',0,18))}

def generate(seed=42,origin_s=5.0,x_km=2.0,y_km=-4.0,velocity=5.0,duration=20.0):
    rng=Random(seed)
    result={}
    for code,s in network().items():
        arrival=origin_s+hypot(s.x_km-x_km,s.y_km-y_km)/velocity
        n=int(duration*s.sample_hz)
        data=[]
        for i in range(n):
            t=i/s.sample_hz
            pulse=2.4*exp(-((t-arrival)/0.15)**2)*sin(2*pi*8*(t-arrival))
            data.append(round(rng.gauss(0,0.035)+pulse,6))
        result[code]=data
    return result
