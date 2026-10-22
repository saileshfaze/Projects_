"""Load synthetic JSONL corrections; re-running is safe via idempotency keys."""

import argparse
import json
import os
from pathlib import Path

from chronos_ledger.audit import verify
from chronos_ledger.models import Correction
from chronos_ledger.service import Ledger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/sample_events.jsonl"))
    parser.add_argument("--db", default=os.getenv("CHRONOS_DB", "./chronos.sqlite3"))
    args = parser.parse_args()
    ledger = Ledger(args.db)
    counts = {}
    with args.input.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                receipt = ledger.correct(
                    record["tenant"], record["entity"],
                    Correction.model_validate(record["correction"]),
                )
                counts["replayed" if receipt.replayed else "created"] = (
                    counts.get("replayed" if receipt.replayed else "created", 0) + 1
                )
            except Exception as exc:
                raise SystemExit(f"line {line_number}: {exc}") from exc
    print(json.dumps({"writes": counts, "db": args.db}, indent=2))
    for tenant in sorted({json.loads(line)["tenant"] for line in args.input.read_text().splitlines() if line.strip()}):
        report = verify(args.db, tenant)
        print(report.model_dump_json())
        if not report.valid:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
