"""Check bundled JSON fixtures against the domain model."""
import json
from pathlib import Path
from skyweave.models import parse_flights

root=Path(__file__).resolve().parents[1]
for name in ('crossing','separated'):
    f=parse_flights(json.loads((root/'data'/f'{name}.json').read_text()))
    print(name,len(f),'validated flights')
