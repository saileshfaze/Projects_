"""Generate deterministic, fictional exposure and conversion events."""
import json, random
from pathlib import Path
from flagship.core import load_flags,evaluate

def generate(output='data/synthetic_events.jsonl', count=500, seed=41):
    rng=random.Random(seed);flag=load_flags('data/flags.json')['new-checkout']
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:
        for i in range(count):
            decision=evaluate(flag,f'synthetic-{i}')
            f.write(json.dumps({'subject':f'synthetic-{i}','variation':decision.variation,'converted':rng.random()<(.15 if decision.variation=='treatment' else .12)})+'\n')
    return p
if __name__=='__main__': print(generate())
