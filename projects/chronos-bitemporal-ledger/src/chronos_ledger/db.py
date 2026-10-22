"""SQLite connection lifecycle and reproducible schema."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS operations (
    operation_id TEXT PRIMARY KEY,
    tenant TEXT NOT NULL,
    entity TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    actor TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    write_digest TEXT NOT NULL,
    closed_rows_json TEXT NOT NULL,
    prev_chain_hash TEXT NOT NULL,
    chain_hash TEXT NOT NULL,
    UNIQUE (tenant, idempotency_key)
);
CREATE INDEX IF NOT EXISTS idx_operations_tenant_order
    ON operations (tenant, recorded_at, operation_id);

CREATE TABLE IF NOT EXISTS record_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant TEXT NOT NULL,
    entity TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT NOT NULL,
    system_from TEXT NOT NULL,
    system_to TEXT,
    payload_json TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    operation_id TEXT NOT NULL REFERENCES operations(operation_id),
    CHECK (valid_from < valid_to),
    CHECK (system_to IS NULL OR system_from < system_to)
);
CREATE INDEX IF NOT EXISTS idx_versions_lookup
    ON record_versions (tenant, entity, valid_from, valid_to, system_from, system_to);
CREATE INDEX IF NOT EXISTS idx_versions_operation
    ON record_versions (operation_id);
"""


def connect(path: str) -> sqlite3.Connection:
    if path != ":memory:":
        Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, isolation_level=None, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    return conn


def initialize(path: str) -> None:
    conn = connect(path)
    try:
        conn.executescript(SCHEMA)
    finally:
        conn.close()
