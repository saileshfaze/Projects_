"""Synthetic factory measurements with known injected shift, drift and spike labels."""
from datetime import datetime,timedelta,timezone
import random
from .models import Reading

def generate(seed:int=2026, baseline_n:int=80, production_n:int=120)->tuple[list[Reading],list[Reading],list[dict]]:
    if baseline_n<8 or production_n<10: raise ValueError('insufficient synthetic sample counts')
    rng=random.Random(seed); start=datetime(2026,1,1,tzinfo=timezone.utc)
    baseline=[];production=[];labels=[]
    for i in range(baseline_n+production_n):
        j=i-baseline_n
        shift=1.25 if j>=production_n//3 else 0.0
        drift=0.016*(j-production_n//2) if j>=production_n//2 else 0.0
        spike=3.6 if j>=0 and j%47==46 else 0.0
        value=round(50.0+shift+drift+spike+rng.gauss(0,0.45),5)
        r=Reading(event_id=f'sim-{seed}-{i:05d}',timestamp=(start+timedelta(minutes=i)).isoformat(),line='line-07',machine='press-03',metric='diameter_mm',lot='baseline' if j<0 else f'lot-{j//40+1:02d}',value=value)
        if j<0: baseline.append(r)
        else:
            production.append(r)
            labels.append({'event_id':r.event_id,'shift':int(shift>0),'drift':int(drift>0),'spike':int(spike>0)})
    return baseline,production,labels
