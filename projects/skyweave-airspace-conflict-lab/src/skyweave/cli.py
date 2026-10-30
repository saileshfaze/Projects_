"""Command-line entrypoint for reproducible scenario analysis."""
import argparse,json
from pathlib import Path
from .models import Thresholds
from .service import analyze
from .reporting import timeline_svg,conflict_csv
from .models import Conflict
from .persistence import Store

def main(argv=None):
    p=argparse.ArgumentParser(description='SkyWeave synthetic airspace analysis')
    p.add_argument('scenario',type=Path)
    p.add_argument('--out',type=Path,default=Path('out'))
    p.add_argument('--samples',type=int,default=100)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--db',type=str,default='skyweave.db')
    args=p.parse_args(argv)
    scenario=json.loads(args.scenario.read_text())
    result=analyze(scenario,Thresholds(),args.samples,args.seed)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    (args.out/'tracks.geojson').write_text(json.dumps(result['geojson'],indent=2)+'\n')
    conflicts=[Conflict(**c) for c in result['conflicts']]
    (args.out/'conflicts.csv').write_text(conflict_csv(conflicts))
    (args.out/'timeline.svg').write_text(timeline_svg(conflicts))
    run_id=Store(args.db).save(scenario,result)
    print(json.dumps({'run_id':run_id,'conflict_count':result['conflict_count'],'output':str(args.out)},indent=2))

if __name__=='__main__':main()
