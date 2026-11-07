"""Brute-force travel-time grid search for a constant-velocity 2-D model."""
from math import hypot, sqrt
from .models import Event

def locate(picks, stations, velocity_km_s=5.0, bounds=(-20,20,-20,20), step_km=2.0):
    if velocity_km_s<=0 or step_km<=0:
        raise ValueError("velocity and step must be positive")
    unique={p.station:p for p in picks}
    if len(unique)<3 or any(s not in stations for s in unique):
        raise ValueError("at least 3 known stations required")
    xmin,xmax,ymin,ymax=bounds
    if xmin>xmax or ymin>ymax:
        raise ValueError("invalid bounds")
    nx=int((xmax-xmin)/step_km)+1
    ny=int((ymax-ymin)/step_km)+1
    if nx*ny>250000:
        raise ValueError("grid too large")
    best=None
    for ix in range(nx):
        x=xmin+ix*step_km
        for iy in range(ny):
            y=ymin+iy*step_km
            origins=[pk.time_s-hypot(stations[code].x_km-x,stations[code].y_km-y)/velocity_km_s for code,pk in unique.items()]
            t=sum(origins)/len(origins)
            rms=sqrt(sum((v-t)**2 for v in origins)/len(origins))
            candidate=(rms,x,y,t)
            if best is None or candidate<best:best=candidate
    rms,x,y,t=best
    return Event(t,x,y,rms,tuple(sorted(unique)))
