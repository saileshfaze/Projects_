import argparse,json,random
from pathlib import Path

def generate(seed=2026,count=100):
    r=random.Random(seed); t=0.0; jobs=[]
    for i in range(count):
        t+=round(r.expovariate(0.6),3)
        jobs.append({'id':f'job-{i:04d}','arrival':round(t,3),'duration':round(r.uniform(.5,4),3)})
    return {'servers':3,'waiting_capacity':20,'synthetic':True,'seed':seed,'jobs':jobs}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=2026);p.add_argument('--count',type=int,default=100);p.add_argument('--output',default='data/generated.json');a=p.parse_args()
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(generate(a.seed,a.count),indent=2)+'\n')
