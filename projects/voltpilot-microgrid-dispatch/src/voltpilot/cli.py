"""Command line entrypoint: generate, run, compare, inspect."""
import argparse
import json
import os
from dataclasses import asdict
from .models import Site
from .synthetic import generate, load_json, save_json
from .dispatch import simulate, compare, STRATEGIES
from .report import save_report
from .storage import store, fetch, list_runs


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(prog="voltpilot")
    sub=parser.add_subparsers(dest="command",required=True)
    g=sub.add_parser("generate",help="generate deterministic synthetic input")
    g.add_argument("--days",type=int,default=2);g.add_argument("--seed",type=int,default=2026)
    g.add_argument("--out",default="data/demo.json");g.add_argument("--outage-start",type=int)
    g.add_argument("--outage-length",type=int,default=0)
    r=sub.add_parser("run",help="simulate and persist a dispatch")
    r.add_argument("--input",default="data/demo.json");r.add_argument("--strategy",choices=STRATEGIES,default="price_aware")
    r.add_argument("--db",default=os.getenv("VOLTPILOT_DB","voltpilot.db"));r.add_argument("--report-dir",default="out")
    c=sub.add_parser("compare",help="compare all four policies")
    c.add_argument("--input",default="data/demo.json")
    q=sub.add_parser("inspect",help="read an existing run and verify its audit chain")
    q.add_argument("run_id");q.add_argument("--db",default=os.getenv("VOLTPILOT_DB","voltpilot.db"))
    l=sub.add_parser("list",help="list saved runs")
    l.add_argument("--db",default=os.getenv("VOLTPILOT_DB","voltpilot.db"))
    args=parser.parse_args(argv)
    if args.command=="generate":
        from pathlib import Path
        Path(args.out).parent.mkdir(parents=True,exist_ok=True)
        profile=generate(args.days,args.seed,args.outage_start,args.outage_length)
        save_json(profile,args.out)
        print(json.dumps({"path":args.out,"intervals":len(profile)}))
    elif args.command=="run":
        site=Site();summary,steps=simulate(load_json(args.input),site,args.strategy)
        run_id=store(args.db,site,summary,steps)
        save_report(args.report_dir,summary,steps,site.battery.capacity_kwh,run_id)
        print(json.dumps({"id":run_id,"summary":asdict(summary)},indent=2))
    elif args.command=="compare":
        print(json.dumps(compare(load_json(args.input),Site()),indent=2))
    elif args.command=="inspect":
        row=fetch(args.db,args.run_id)
        if row is None:
            parser.error("run not found")
        print(json.dumps(row,indent=2))
    elif args.command=="list":
        print(json.dumps(list_runs(args.db),indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
