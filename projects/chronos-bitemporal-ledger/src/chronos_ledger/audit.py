"""Audit checks: chained operation metadata and immutable version contents."""

import json

from .db import connect
from .models import AuditReport
from .service import chain_digest, digest, write_digest


def verify(path: str, tenant: str) -> AuditReport:
    conn = connect(path)
    problems: list[str] = []
    try:
        operations = conn.execute(
            "SELECT * FROM operations WHERE tenant=? ORDER BY recorded_at, operation_id",
            (tenant,),
        ).fetchall()
        versions = conn.execute(
            "SELECT * FROM record_versions WHERE tenant=?", (tenant,),
        ).fetchall()
        by_operation: dict[str, list[dict]] = {}
        for version in versions:
            row = dict(version)
            if digest(row["payload_json"]) != row["payload_hash"]:
                problems.append(f"payload hash mismatch for version {row['id']}")
            by_operation.setdefault(row["operation_id"], []).append(row)
        prev = "0" * 64
        expected_closures: dict[int, str] = {}
        for op in operations:
            if op["prev_chain_hash"] != prev:
                problems.append(f"broken chain predecessor at {op['operation_id']}")
            op_versions = by_operation.pop(op["operation_id"], [])
            if write_digest(op_versions) != op["write_digest"]:
                problems.append(f"version digest mismatch at {op['operation_id']}")
            try:
                closed = json.loads(op["closed_rows_json"])
                if closed != sorted(set(closed)):
                    problems.append(f"noncanonical closure list at {op['operation_id']}")
                for row_id in closed:
                    if row_id in expected_closures:
                        problems.append(f"duplicate closure for version {row_id}")
                    expected_closures[row_id] = op["recorded_at"]
                    closed_row = conn.execute(
                        "SELECT system_to FROM record_versions WHERE id=? AND tenant=?",
                        (row_id, tenant),
                    ).fetchone()
                    if not closed_row or closed_row["system_to"] != op["recorded_at"]:
                        problems.append(f"closure mismatch for version {row_id}")
                closures = digest(op["closed_rows_json"])
                expected = chain_digest(
                    prev, op["operation_id"], op["recorded_at"],
                    op["request_hash"], op["write_digest"], closures,
                    op["actor"], op["tenant"], op["entity"], op["idempotency_key"],
                )
                if expected != op["chain_hash"]:
                    problems.append(f"chain hash mismatch at {op['operation_id']}")
            except (TypeError, ValueError) as exc:
                problems.append(f"invalid closure list: {exc}")
            prev = op["chain_hash"]
        for row in versions:
            if row["system_to"] != expected_closures.get(row["id"]):
                problems.append(f"unexpected system_to for version {row['id']}")
        for unknown in by_operation:
            problems.append(f"orphaned versions for operation {unknown}")
        return AuditReport(
            tenant=tenant, operations=len(operations), versions=len(versions),
            valid=not problems, problems=problems,
        )
    finally:
        conn.close()
