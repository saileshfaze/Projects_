"""Small synthetic runtime probe; not a performance guarantee."""
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from hydrograph.model import from_dict
from hydrograph.solver import solve
n=from_dict(json.loads((Path(__file__).parents[1]/'data/network.json').read_text()))
t=time.perf_counter()
for _ in range(100): assert solve(n).converged
print(f'100 synthetic solves: {time.perf_counter()-t:.4f} seconds (local only)')
