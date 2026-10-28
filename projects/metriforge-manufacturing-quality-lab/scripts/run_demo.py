"""Run a full deterministic local scenario and write auditable artifacts."""
import json
from pathlib import Path
from metriforge.models import QualitySpec
from metriforge.synthetic import generate
from metriforge.service import QualityService
from metriforge.report import save_json,save_svg

def run(out='reports',db='state/demo.sqlite'):
    path=Path(db);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists(): path.unlink()
    service=QualityService(db);service.set_spec(QualitySpec('diameter_mm',48,52,50,'mm'))
    baseline,production,_=generate()
    print('baseline',service.ingest(baseline))
    print('production',service.ingest(production))
    report=service.report('line-07','press-03','diameter_mm')
    folder=Path(out);save_json(report,str(folder/'quality-report.json'));save_svg(report,str(folder/'control-chart.svg'))
    summary={'events':service.audit()['events'],'audit_valid':service.audit()['valid'],'readings':report['production_count'],'signals':len(report['signals']),'lot_tiers':{k:v['tier'] for k,v in report['lots'].items()}}
    (folder/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    return summary
if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
