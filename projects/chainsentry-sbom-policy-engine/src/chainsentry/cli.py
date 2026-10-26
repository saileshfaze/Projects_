"""Command-line interface with machine-readable JSON output and CI exit codes."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .service import scan
from .store import ScanStore, diff_reports


def read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="chainsentry", description="Offline SBOM policy evaluation")
    sub = parser.add_subparsers(dest="command", required=True)
    scan_cmd = sub.add_parser("scan")
    scan_cmd.add_argument("--sbom", required=True)
    scan_cmd.add_argument("--feed", required=True)
    scan_cmd.add_argument("--policy", required=True)
    scan_cmd.add_argument("--db")
    scan_cmd.add_argument("--project", default="demo")
    history_cmd = sub.add_parser("history")
    history_cmd.add_argument("--db", required=True)
    history_cmd.add_argument("--project", required=True)
    diff_cmd = sub.add_parser("diff")
    diff_cmd.add_argument("--db", required=True)
    diff_cmd.add_argument("--before", type=int, required=True)
    diff_cmd.add_argument("--after", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            report = scan(read_json(args.sbom), read_json(args.feed), read_json(args.policy))
            payload = report.to_dict()
            if args.db:
                payload["scan_id"] = ScanStore(args.db).save(args.project, report)
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 2 if report.status == "fail" else 0
        if args.command == "history":
            print(json.dumps(ScanStore(args.db).history(args.project), indent=2))
            return 0
        db = ScanStore(args.db)
        before, after = db.get(args.before), db.get(args.after)
        if before is None or after is None:
            raise ValueError("scan not found")
        if before["project"] != after["project"]:
            raise ValueError("different projects")
        print(json.dumps(diff_reports(before["report"], after["report"]), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"chainsentry: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
