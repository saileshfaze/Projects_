"""Export a tenant audit report for independent retention."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from chronos_ledger.audit import verify
from chronos_ledger.db import connect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.db, args.tenant)
    conn = connect(args.db)
    try:
        row = conn.execute(
            "SELECT chain_hash, operation_id FROM operations WHERE tenant=? "
            "ORDER BY recorded_at DESC LIMIT 1", (args.tenant,),
        ).fetchone()
    finally:
        conn.close()
    document = {
        "tenant": args.tenant,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "latest_chain_hash": row["chain_hash"] if row else None,
        "latest_operation_id": row["operation_id"] if row else None,
        "audit": report.model_dump(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    if not report.valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
