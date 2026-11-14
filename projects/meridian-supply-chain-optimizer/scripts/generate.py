import json,random,argparse
from pathlib import Path

def generate(seed=2026,n=8):
    rng=random.Random(seed)
    supply={f'W{i}':rng.randint(5,15) for i in range(n)}
    demand={f'S{i}':rng.randint(4,12) for i in range(n)}
    routes=[{'source':a,'destination':b,'capacity':rng.randint(3,14),'unit_cost':rng.randint(1,20)} for a in supply for b in demand]
    return {'supply':supply,'demand':demand,'routes':routes,'synthetic':True,'seed':seed}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=2026);p.add_argument('--size',type=int,default=8);p.add_argument('--output',default='data/generated.json');a=p.parse_args()
    target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(generate(a.seed,a.size),indent=2)+'\n')
