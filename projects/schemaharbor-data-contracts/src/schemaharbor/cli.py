"""Command-line entry point. JSON output suitable for CI gating."""
import argparse
import csv
import json
from pathlib import Path
from .contracts import Contract
from .compatibility import compare, recommendation
from .validation import profile
from .lineage import impacted

def main(argv=None):
    parser = argparse.ArgumentParser(prog="schemaharbor")
    sub = parser.add_subparsers(dest="command", required=True)
    diff = sub.add_parser("diff")
    diff.add_argument("old"); diff.add_argument("new")
    diff.add_argument("--fail-breaking", action="store_true")
    check = sub.add_parser("check")
    check.add_argument("contract"); check.add_argument("csv")
    check.add_argument("--allow-unknown", action="store_true")
    deps = sub.add_parser("impact")
    deps.add_argument("graph"); deps.add_argument("changed")
    args = parser.parse_args(argv)
    if args.command == "diff":
        changes = compare(Contract.load(args.old), Contract.load(args.new))
        result = {"recommended_bump": recommendation(changes), "changes": [c.to_dict() for c in changes]}
        code = 2 if args.fail_breaking and result["recommended_bump"] == "major" else 0
    elif args.command == "check":
        with Path(args.csv).open(newline="", encoding="utf-8") as f:
            result = profile(Contract.load(args.contract), csv.DictReader(f), not args.allow_unknown)
        code = 1 if result["valid_rows"] != result["rows"] else 0
    else:
        graph = json.loads(Path(args.graph).read_text(encoding="utf-8"))
        result = {"changed": args.changed, "impacted": impacted(graph["edges"], args.changed)}
        code = 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
