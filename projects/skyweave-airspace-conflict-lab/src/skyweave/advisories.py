"""What-if schedule offsets; these are not operational air traffic instructions."""
from dataclasses import asdict
from .models import Flight,Fix,Thresholds
from .detector import detect

def shift_flight(f:Flight,seconds:float)->Flight:
    return Flight(f.callsign,tuple(Fix(p.t+seconds,p.lat,p.lon,p.alt_ft) for p in f.fixes))

def suggest_delays(flights:tuple[Flight,...],thresholds:Thresholds=Thresholds(),offsets:tuple[int,...]=(30,60,90,120))->list[dict]:
    base=len(detect(flights,thresholds)); results=[]
    for target in flights:
        for delay in offsets:
            changed=tuple(shift_flight(f,delay) if f.callsign==target.callsign else f for f in flights)
            count=len(detect(changed,thresholds))
            results.append({'callsign':target.callsign,'delay_s':delay,'conflicts_after':count,'conflicts_before':base,'improvement':base-count})
    return sorted(results,key=lambda r:(-r['improvement'],r['delay_s'],r['callsign']))
