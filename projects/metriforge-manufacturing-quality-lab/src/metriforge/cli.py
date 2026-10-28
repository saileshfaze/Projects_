"""CLI for synthetic generation, loading, analysis and audit verification."""
import argparse,csv,json
from pathlib import Path
from .models import QualitySpec
from .synthetic import generate
from .csvio import save_readings,load_readings
from .service import QualityService
from .report import save_json,save_svg

def main(argv=None):
    parser=argparse.ArgumentParser(prog='metriforge')
    parser.add_argument('--db',default='state/metriforge.sqlite')
    sub=parser.add_subparsers(dest='command',required=True)
    g=sub.add_parser('generate');g.add_argument('--out',default='data/synthetic');g.add_argument('--seed',type=int,default=2026)
    load=sub.add_parser('load');load.add_argument('csv')
    a=sub.add_parser('analyze');a.add_argument('--out',default='reports')
    sub.add_parser('audit')
    args=parser.parse_args(argv)
    if args.command=='generate':
        base,prod,labels=generate(seed=args.seed);folder=Path(args.out);folder.mkdir(parents=True,exist_ok=True)
        save_readings(str(folder/'baseline.csv'),base);save_readings(str(folder/'production.csv'),prod)
        with (folder/'labels.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=['event_id','shift','drift','spike']);writer.writeheader();writer.writerows(labels)
        print(json.dumps({'baseline':len(base),'production':len(prod),'labels':len(labels)}));return
    service=QualityService(args.db)
    if args.command=='load':
        service.set_spec(QualitySpec('diameter_mm',48,52,50,'mm'))
        print(json.dumps(service.ingest(load_readings(args.csv))));return
    if args.command=='audit': print(json.dumps(service.audit(),sort_keys=True));return
    if args.command=='analyze':
        report=service.report('line-07','press-03','diameter_mm')
        folder=Path(args.out);save_json(report,str(folder/'quality-report.json'));save_svg(report,str(folder/'control-chart.svg'))
        print(json.dumps({'readings':report['production_count'],'signals':len(report['signals']),'lots':report['lots']},sort_keys=True));return
if __name__=='__main__':main()
