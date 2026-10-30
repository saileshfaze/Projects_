"""Deterministic synthetic regional scenarios; no real flight telemetry."""
from .models import Flight,Fix

def crossing()->tuple[Flight,...]:
    return (
        Flight('SW101',(Fix(0,40.000,-74.060,30000),Fix(600,40.000,-73.940,30000))),
        Flight('SW202',(Fix(0,39.950,-74.000,30500),Fix(600,40.050,-74.000,30500))),
        Flight('SW303',(Fix(0,40.150,-74.120,34000),Fix(600,40.150,-73.880,34000))),
        Flight('SW404',(Fix(720,39.950,-74.000,30000),Fix(1320,40.050,-74.000,30000))),
    )

def separated()->tuple[Flight,...]:
    return (
        Flight('SEP1',(Fix(0,40,-74,30000),Fix(600,40,-73.9,30000))),
        Flight('SEP2',(Fix(0,40.2,-74,30000),Fix(600,40.2,-73.9,30000))),
    )
