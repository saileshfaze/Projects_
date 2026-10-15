-- SQLite reference schema: tenant-scoped unique event IDs and event-time indexes.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS events (
    tenant TEXT NOT NULL,
    event_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    occurred_ms INTEGER NOT NULL,
    received_ms INTEGER NOT NULL,
    value REAL NOT NULL,
    attributes_json TEXT NOT NULL,
    PRIMARY KEY (tenant, event_id)
);
CREATE INDEX IF NOT EXISTS idx_events_window
    ON events (tenant, occurred_ms, event_type);
CREATE TABLE IF NOT EXISTS watermarks (
    tenant TEXT PRIMARY KEY,
    max_occurred_ms INTEGER NOT NULL
);
