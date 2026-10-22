"""Command-line ingestion, temporal query and audit validation."""

import argparse
import json
import os
from datetime import date, datetime
from pathlib import Path

from .audit import verify
from .models import Correction
from .service import Ledger


def main() -> None:
    parser = argparse.ArgumentParser(prog="chronos-ledger")
    parser.add_argument("--db", default=os.getenv("CHRONOS_DB", "./chronos.sqlite3"))
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="Read one JSON correction per line")
    ingest.add_argument("path", type=Path)
    query = commands.add_parser("query", help="Reconstruct a bitemporal snapshot")
    query.add_argument("tenant")
    query.add_argument("entity")
    query.add_argument("valid_at", type=date.fromisoformat)
    query.add_argument("--known-at", type=datetime.fromisoformat)
    audit = commands.add_parser("audit", help="Validate the tenant hash chain")
    audit.add_argument("tenant")
    args = parser.parse_args()
    ledger = Ledger(args.db)
    if args.command == "ingest":
        with args.path.open(encoding="utf-8") as source:
            for number, line in enumerate(source, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    change = Correction.model_validate(record["correction"])
                    result = ledger.correct(record["tenant"], record["entity"], change)
                except (KeyError, ValueError) as exc:
                    raise SystemExit(f"line {number}: {exc}") from exc
                print(result.model_dump_json())
    elif args.command == "query":
        result = ledger.snapshot(args.tenant, args.entity, args.valid_at, args.known_at)
        print(result.model_dump_json(indent=2))
    else:
        report = verify(args.db, args.tenant)
        print(report.model_dump_json(indent=2))
        if not report.valid:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
