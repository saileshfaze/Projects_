"""Piecewise linear interpolation, with no extrapolation outside a flight plan."""
from .models import Flight, Fix

def at(flight:Flight,t:float)->Fix|None:
    if t<flight.fixes[0].t or t>flight.fixes[-1].t:
        return None
    for a,b in zip(flight.fixes,flight.fixes[1:]):
        if a.t<=t<=b.t:
            w=(t-a.t)/(b.t-a.t)
            return Fix(t, a.lat+w*(b.lat-a.lat),a.lon+w*(b.lon-a.lon),a.alt_ft+w*(b.alt_ft-a.alt_ft))
    return flight.fixes[-1]

def intervals(flight:Flight)->list[tuple[Fix,Fix]]:
    return list(zip(flight.fixes,flight.fixes[1:]))
