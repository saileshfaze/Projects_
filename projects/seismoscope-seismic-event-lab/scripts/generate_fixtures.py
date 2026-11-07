"""Generate synthetic traces and event report with deterministic seeds."""
import json
from pathlib import Path
from seismoscope.synthetic import generate,network
from seismoscope.pipeline import run

def main():
    out=Path('data/generated');out.mkdir(parents=True,exist_ok=True)
    (out/'stations.json').write_text(json.dumps({k:vars(v) for k,v in network().items()},indent=2)+'\n')
    (out/'traces.json').write_text(json.dumps(generate(seed=42))+'\n')
    (out/'events.json').write_text(json.dumps(run(seed=42),indent=2)+'\n')
if __name__=='__main__':main()
