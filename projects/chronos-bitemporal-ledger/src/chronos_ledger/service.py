"""Transactional bitemporal correction engine.

Valid time: when a fact was effective. System time: when the database knew it.
"""

import hashlib
import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from typing import Callable
from uuid import uuid4

from .db import connect, initialize
from .models import Correction, EntitySnapshot, Receipt
from .service_queries import QueryMixin, SnapshotNotFound


class IdempotencyConflict(ValueError):
    """The same tenant/key was reused with different request content."""


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def row_signature(row: dict) -> list[str]:
    return [
        row["tenant"], row["entity"], row["valid_from"], row["valid_to"],
        row["system_from"], row["payload_hash"], row["operation_id"],
    ]


def write_digest(rows: list[dict]) -> str:
    return digest(canonical(sorted(row_signature(r) for r in rows)))


def chain_digest(
    previous: str, operation_id: str, recorded_at: str, request_hash: str,
    writes: str, closures: str, actor: str, tenant: str, entity: str, idempotency_key: str,
) -> str:
    return digest(canonical([
        previous, operation_id, recorded_at, request_hash, writes, closures,
        actor, tenant, entity, idempotency_key,
    ]))


class Ledger(QueryMixin):
    def __init__(self, path: str, clock: Callable[[], datetime] | None = None) -> None:
        self.path = path
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        initialize(path)

    def _timestamp(self, conn: sqlite3.Connection, tenant: str) -> str:
        now = self.clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("clock must return an aware datetime")
        now = now.astimezone(timezone.utc)
        latest = conn.execute(
            "SELECT recorded_at FROM operations WHERE tenant=? "
            "ORDER BY recorded_at DESC LIMIT 1", (tenant,),
        ).fetchone()
        if latest and now <= datetime.fromisoformat(latest["recorded_at"]):
            now = datetime.fromisoformat(latest["recorded_at"]) + timedelta(microseconds=1)
        return now.isoformat(timespec="microseconds")

    @staticmethod
    def _remainder_strings(
        old_start: str, old_end: str, new_start: str, new_end: str,
    ) -> list[tuple[str, str]]:
        parts = []
        if old_start < new_start:
            parts.append((old_start, min(old_end, new_start)))
        if new_end < old_end:
            parts.append((max(old_start, new_end), old_end))
        return parts

    def correct(self, tenant: str, entity: str, change: Correction) -> Receipt:
        if not tenant or not entity:
            raise ValueError("tenant and entity must not be empty")
        start, end = change.valid_from.isoformat(), change.valid_to.isoformat()
        request_hash = digest(canonical({
            "tenant": tenant, "entity": entity, "change": change.model_dump(mode="json"),
        }))
        conn = connect(self.path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT * FROM operations WHERE tenant=? AND idempotency_key=?",
                (tenant, change.idempotency_key),
            ).fetchone()
            if existing:
                if existing["request_hash"] != request_hash:
                    raise IdempotencyConflict("idempotency key already belongs to another request")
                conn.commit()
                return Receipt(
                    operation_id=existing["operation_id"],
                    recorded_at=datetime.fromisoformat(existing["recorded_at"]),
                    chain_hash=existing["chain_hash"], replayed=True,
                )
            timestamp = self._timestamp(conn, tenant)
            operation_id = str(uuid4())
            payload_json = canonical(change.payload)
            payload_hash = digest(payload_json)
            old_rows = conn.execute(
                "SELECT * FROM record_versions WHERE tenant=? AND entity=? "
                "AND system_to IS NULL AND valid_from < ? AND valid_to > ? "
                "ORDER BY valid_from, id", (tenant, entity, end, start),
            ).fetchall()
            new_rows: list[dict] = []
            closed_ids: list[int] = []
            for old in old_rows:
                closed_ids.append(old["id"])
                for left, right in self._remainder_strings(
                    old["valid_from"], old["valid_to"], start, end,
                ):
                    new_rows.append({
                        "tenant": tenant, "entity": entity,
                        "valid_from": left, "valid_to": right,
                        "system_from": timestamp, "payload_json": old["payload_json"],
                        "payload_hash": old["payload_hash"], "operation_id": operation_id,
                    })
            new_rows.append({
                "tenant": tenant, "entity": entity, "valid_from": start, "valid_to": end,
                "system_from": timestamp, "payload_json": payload_json,
                "payload_hash": payload_hash, "operation_id": operation_id,
            })
            for old_id in closed_ids:
                conn.execute(
                    "UPDATE record_versions SET system_to=? WHERE id=? AND system_to IS NULL",
                    (timestamp, old_id),
                )
            previous = conn.execute(
                "SELECT chain_hash FROM operations WHERE tenant=? "
                "ORDER BY recorded_at DESC LIMIT 1", (tenant,),
            ).fetchone()
            prev_hash = previous["chain_hash"] if previous else "0" * 64
            closures_json = canonical(sorted(closed_ids))
            writes = write_digest(new_rows)
            chain_hash = chain_digest(
                prev_hash, operation_id, timestamp, request_hash, writes,
                digest(closures_json), change.actor, tenant, entity, change.idempotency_key,
            )
            conn.execute(
                "INSERT INTO operations (operation_id, tenant, entity, idempotency_key, "
                "actor, recorded_at, request_hash, write_digest, closed_rows_json, "
                "prev_chain_hash, chain_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (operation_id, tenant, entity, change.idempotency_key, change.actor,
                 timestamp, request_hash, writes, closures_json, prev_hash, chain_hash),
            )
            for row in new_rows:
                conn.execute(
                    "INSERT INTO record_versions "
                    "(tenant, entity, valid_from, valid_to, system_from, payload_json, "
                    "payload_hash, operation_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (row["tenant"], row["entity"], row["valid_from"], row["valid_to"],
                     row["system_from"], row["payload_json"], row["payload_hash"],
                     row["operation_id"]),
                )
            conn.commit()
            return Receipt(
                operation_id=operation_id,
                recorded_at=datetime.fromisoformat(timestamp), chain_hash=chain_hash,
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

