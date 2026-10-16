PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS feature_views (
    name TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    fields_json TEXT NOT NULL,
    ttl_seconds INTEGER NOT NULL CHECK (ttl_seconds > 0),
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    PRIMARY KEY (name, version)
);

CREATE TABLE IF NOT EXISTS feature_events (
    event_id TEXT PRIMARY KEY,
    view_name TEXT NOT NULL,
    version INTEGER NOT NULL,
    entity_key TEXT NOT NULL,
    event_ts TEXT NOT NULL,
    available_ts TEXT NOT NULL,
    values_json TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    FOREIGN KEY (view_name, version) REFERENCES feature_views(name, version)
);

CREATE INDEX IF NOT EXISTS ix_feature_history
    ON feature_events(view_name, version, entity_key, event_ts DESC, available_ts DESC);

CREATE TABLE IF NOT EXISTS online_features (
    view_name TEXT NOT NULL,
    version INTEGER NOT NULL,
    entity_key TEXT NOT NULL,
    event_id TEXT NOT NULL,
    event_ts TEXT NOT NULL,
    available_ts TEXT NOT NULL,
    values_json TEXT NOT NULL,
    materialized_at TEXT NOT NULL,
    PRIMARY KEY (view_name, version, entity_key),
    FOREIGN KEY (event_id) REFERENCES feature_events(event_id)
);

CREATE TABLE IF NOT EXISTS materialization_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    view_name TEXT NOT NULL,
    version INTEGER NOT NULL,
    as_of TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    completed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    subject TEXT NOT NULL,
    detail_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);
