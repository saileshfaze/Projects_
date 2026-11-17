"""Deterministic fictional documentation corpus generator."""
import argparse,json,random
from pathlib import Path
WORDS='database query indexing search latency throughput storage cache transaction reliability replication monitoring pipeline vector shard'.split()
def generate(count=100,seed=2026):
    rng=random.Random(seed)
    for n in range(count):
        yield {'id':f'doc-{n:05d}','title':f'Synthetic note {n}','body':' '.join(rng.choices(WORDS,k=rng.randint(15,60)))}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--count',type=int,default=100);p.add_argument('--seed',type=int,default=2026);p.add_argument('--output',default='data/generated.jsonl');a=p.parse_args()
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:
        for row in generate(a.count,a.seed):f.write(json.dumps(row)+'\n')
