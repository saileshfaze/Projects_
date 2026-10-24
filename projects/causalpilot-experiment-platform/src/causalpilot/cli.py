"""Command-line reproducibility entry points."""
import argparse
import json
import os
from .models import Experiment
from .service import ExperimentService
from .synthetic import generate, read_csv, write_csv


def main() -> None:
    parser=argparse.ArgumentParser(prog="causalpilot")
    parser.add_argument("--db",default=os.getenv("CAUSALPILOT_DB","causalpilot.sqlite3"))
    sub=parser.add_subparsers(dest="command",required=True)
    init=sub.add_parser("init")
    init.add_argument("experiment_id")
    init.add_argument("--salt",required=True)
    gen=sub.add_parser("generate")
    gen.add_argument("experiment_id")
    gen.add_argument("--salt",required=True)
    gen.add_argument("--n",type=int,default=800)
    gen.add_argument("--output",default="data/events.csv")
    ingest=sub.add_parser("ingest")
    ingest.add_argument("path")
    report=sub.add_parser("report")
    report.add_argument("experiment_id")
    args=parser.parse_args()
    svc=ExperimentService(args.db)
    if args.command=="init":
        svc.register(Experiment(args.experiment_id,args.salt))
        print(f"registered {args.experiment_id}")
    elif args.command=="generate":
        cfg=Experiment(args.experiment_id,args.salt)
        svc.register(cfg)
        write_csv(generate(cfg,args.n),args.output)
        print(args.output)
    elif args.command=="ingest":
        created=sum(svc.ingest(e) for e in read_csv(args.path))
        print(f"ingested {created} new events")
    else:
        print(json.dumps(svc.report(args.experiment_id),indent=2))


if __name__=="__main__":
    main()
