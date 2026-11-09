"""Reproducible scenario fixture generation."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from hydrograph.model import from_dict
from hydrograph.scenarios import scaled
from hydrograph.model import to_dict
root=Path(__file__).parents[1]
base=from_dict(json.loads((root/'data/network.json').read_text()))
for name,factors in [('peak',{'A':1.6,'B':1.4,'C':1.3}),('offpeak',{'A':0.5,'B':0.6,'C':0.4})]:
    (root/'data'/f'{name}.json').write_text(json.dumps(to_dict(scaled(base,factors)),indent=2)+'\n')
print('Generated 2 deterministic synthetic scenarios')
