"""Reproducible single-process ingestion smoke benchmark."""

import argparse
import json
import sys
import time
from pathlib import Path

from chronos_ledger.audit import verify
from chronos_ledger.models import Correction
from chronos_ledger.service import Ledger

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_dataset import generate  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=100)
    parser.add_argument("--db", type=Path, default=Path("/tmp/chronos-benchmark.sqlite3"))
    args = parser.parse_args()
    if args.events < 1:
        parser.error("events must be positive")
    if args.db.exists():
        parser.error("refusing to overwrite an existing benchmark database")
    records = generate(seed=42, tenants=1, entities=args.events, revisions=1)
    ledger = Ledger(str(args.db))
    started = time.perf_counter()
    for record in records:
        ledger.correct(record["tenant"], record["entity"], Correction.model_validate(record["correction"]))
    elapsed = time.perf_counter() - started
    report = verify(str(args.db), "tenant-00")
    print(json.dumps({
        "events": len(records), "seconds": round(elapsed, 4),
        "events_per_second": round(len(records) / elapsed, 2),
        "audit_valid": report.valid, "db": str(args.db),
    }, indent=2))
    if not report.valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
