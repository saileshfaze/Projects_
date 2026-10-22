"""Historical reads separated from transactional correction logic."""

import json
from datetime import date, datetime, timezone

from .db import connect
from .models import EntitySnapshot


class SnapshotNotFound(LookupError):
    """No entity version covers the requested point in both timelines."""


class QueryMixin:
    """Read-only historical queries for a ledger with a clock and database path."""

    def snapshot(
        self, tenant: str, entity: str, valid_at: date,
        known_at: datetime | None = None,
    ) -> EntitySnapshot:
        known_at = known_at or self.clock()
        if known_at.tzinfo is None or known_at.utcoffset() is None:
            raise ValueError("known_at must be timezone-aware")
        timestamp = known_at.astimezone(timezone.utc).isoformat(timespec="microseconds")
        conn = connect(self.path)
        try:
            rows = conn.execute(
                "SELECT * FROM record_versions WHERE tenant=? AND entity=? "
                "AND valid_from <= ? AND valid_to > ? AND system_from <= ? "
                "AND (system_to IS NULL OR system_to > ?) ORDER BY id",
                (tenant, entity, valid_at.isoformat(), valid_at.isoformat(), timestamp, timestamp),
            ).fetchall()
            if not rows:
                raise SnapshotNotFound("no version exists at the requested valid/system time")
            if len(rows) != 1:
                raise RuntimeError("integrity violation: multiple versions cover one point")
            row = rows[0]
            return EntitySnapshot(
                tenant=tenant, entity=entity, valid_at=valid_at,
                known_at=datetime.fromisoformat(timestamp),
                payload=json.loads(row["payload_json"]),
                valid_from=date.fromisoformat(row["valid_from"]),
                valid_to=date.fromisoformat(row["valid_to"]),
                system_from=datetime.fromisoformat(row["system_from"]),
                operation_id=row["operation_id"],
            )
        finally:
            conn.close()

    def history(self, tenant: str, entity: str) -> list[dict]:
        conn = connect(self.path)
        try:
            rows = conn.execute(
                "SELECT id, valid_from, valid_to, system_from, system_to, "
                "payload_json, operation_id FROM record_versions "
                "WHERE tenant=? AND entity=? ORDER BY system_from, valid_from, id",
                (tenant, entity),
            ).fetchall()
            return [
                {**{key: row[key] for key in row.keys() if key != "payload_json"},
                 "payload": json.loads(row["payload_json"])}
                for row in rows
            ]
        finally:
            conn.close()
