"""SQLite event store with atomic deduplication and watermark updates."""
from contextlib import contextmanager
from datetime import datetime, timezone
from importlib.resources import files
import json
from pathlib import Path
import sqlite3
import time
from typing import Iterator

from .models import Event


def milliseconds(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


class EventStore:
    def __init__(self, path: str | Path, allowed_lateness_seconds: int = 3600):
        self.path = str(path)
        self.allowed_lateness_ms = allowed_lateness_seconds * 1000
        if self.allowed_lateness_ms < 0:
            raise ValueError("allowed lateness must not be negative")

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        schema = files("pulsemesh").joinpath("sql/schema.sql").read_text()
        with self.connect() as conn:
            conn.executescript(schema)
            if self.path != ":memory:":
                conn.execute("PRAGMA journal_mode=WAL")

    def ingest(self, tenant: str, event: Event) -> str:
        occurred_ms = milliseconds(event.occurred_at)
        received_ms = int(time.time() * 1000)
        if occurred_ms > received_ms + 300_000:
            raise ValueError("Event timestamp is more than five minutes in the future")
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute(
                "SELECT 1 FROM events WHERE tenant=? AND event_id=?",
                (tenant, event.event_id),
            ).fetchone():
                return "duplicate"
            watermark = conn.execute(
                "SELECT max_occurred_ms FROM watermarks WHERE tenant=?", (tenant,)
            ).fetchone()
            if watermark and occurred_ms < watermark["max_occurred_ms"] - self.allowed_lateness_ms:
                return "late"
            conn.execute(
                """INSERT INTO events
                (tenant, event_id, event_type, schema_version, occurred_ms,
                 received_ms, value, attributes_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    tenant, event.event_id, event.event_type, event.schema_version,
                    occurred_ms, received_ms, event.value,
                    json.dumps(event.attributes, sort_keys=True),
                ),
            )
            conn.execute(
                """INSERT INTO watermarks (tenant, max_occurred_ms) VALUES (?, ?)
                ON CONFLICT(tenant) DO UPDATE SET max_occurred_ms =
                MAX(max_occurred_ms, excluded.max_occurred_ms)""",
                (tenant, occurred_ms),
            )
            return "accepted"

    def windows(
        self, tenant: str, start: datetime, end: datetime, window_seconds: int
    ) -> list[dict]:
        start_ms, end_ms = milliseconds(start), milliseconds(end)
        window_ms = window_seconds * 1000
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT (occurred_ms / ?) * ? AS bucket_ms,
                          event_type, COUNT(*) AS count, SUM(value) AS total_value
                   FROM events
                   WHERE tenant=? AND occurred_ms >= ? AND occurred_ms < ?
                   GROUP BY bucket_ms, event_type
                   ORDER BY bucket_ms, event_type""",
                (window_ms, window_ms, tenant, start_ms, end_ms),
            ).fetchall()
        return [
            {
                "bucket_start": datetime.fromtimestamp(
                    row["bucket_ms"] / 1000, tz=timezone.utc
                ),
                "event_type": row["event_type"],
                "count": row["count"],
                "total_value": row["total_value"],
            }
            for row in rows
        ]

    def count(self, tenant: str) -> int:
        with self.connect() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM events WHERE tenant=?", (tenant,)
            ).fetchone()[0]
