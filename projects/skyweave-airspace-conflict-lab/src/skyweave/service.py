"""Composition layer for detection, risk sampling, advisories and persistence."""
from dataclasses import asdict
from .models import Thresholds,parse_flights,flights_payload
from .detector import detect
from .uncertainty import sample_risk
from .advisories import suggest_delays
from .reporting import geojson

def analyze(payload:dict,thresholds:Thresholds=Thresholds(),samples:int=0,seed:int=42)->dict:
    flights=parse_flights(payload)
    conflicts=detect(flights,thresholds)
    result={'flight_count':len(flights),'conflict_count':len(conflicts),'thresholds':asdict(thresholds),'conflicts':[asdict(c) for c in conflicts], 'advisories':suggest_delays(flights,thresholds)[:8], 'geojson':geojson(flights)}
    if samples:
        result['risk']=sample_risk(flights,thresholds,samples,seed).to_dict()
    return result
