"""Create fictional requests using a reproducible seed."""
import argparse
import json
import random
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seed',type=int,default=2026)
    p.add_argument('--count',type=int,default=100)
    p.add_argument('--output',type=Path,default=Path('artifacts/requests.json'))
    a=p.parse_args()
    if a.count < 0: p.error('count must be nonnegative')
    rng=random.Random(a.seed)
    requests=[]
    for i in range(a.count):
        requests.append({'action':rng.choice(['read','write','delete']), 'resource':rng.choice(['document:public','document:internal','document:restricted']), 'subject':{'id':f'fictional-{i:05d}','role':rng.choice(['viewer','editor','admin']),'clearance':rng.randrange(4)},'environment':{'mfa':rng.choice([True,False])}})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(requests,indent=2)+'\n')
if __name__=='__main__':main()
