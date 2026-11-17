"""Create fictional hourly outdoor temperature profiles with a reproducible seed."""
import argparse,json,math,random
from pathlib import Path

def generate(seed=2026,hours=48):
    if hours<1:raise ValueError('hours must be positive')
    rng=random.Random(seed)
    return {'synthetic':True,'seed':seed,'building':{'resistance_k_per_kw':2.,'capacitance_kwh_per_k':4.,'heating_capacity_kw':3.,'cooling_capacity_kw':2.,'initial_temp_c':19.},'weather':[{'outdoor_c':round(9+7*math.sin(2*math.pi*(h%24)/24)+rng.uniform(-.5,.5),3),'internal_kw':.3 if 8<=h%24<20 else .1,'price_per_kwh':.35 if 17<=h%24<22 else .18} for h in range(hours*4)]}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=2026);p.add_argument('--hours',type=int,default=48);p.add_argument('--output',default='data/generated.json');a=p.parse_args()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(generate(a.seed,a.hours),indent=2)+'\n')
