from flagship.core import load_flags,evaluate
from flagship.metrics import summarize
from flagship.audit import append,verify
from pathlib import Path
import json,tempfile
flags=load_flags('data/flags.json')
print('Evaluation:',evaluate(flags['new-checkout'],'demo-user'))
with tempfile.TemporaryDirectory() as d:
    p=str(Path(d)/'audit.jsonl')
    for i in range(100):
        decision=evaluate(flags['new-checkout'],f'synthetic-{i}')
        append(p,{'subject':f'synthetic-{i}','variation':decision.variation})
    assert verify(p)
    print('Audit chain verified: 100 synthetic events')
