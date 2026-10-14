PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    row_count INTEGER NOT NULL CHECK (row_count >= 0),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL REFERENCES datasets(id),
    model_name TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    seed INTEGER NOT NULL,
    config_json TEXT NOT NULL,
    idempotency_key TEXT UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('registered','evaluated','promoted','archived','rejected')),
    metrics_json TEXT,
    drift_psi REAL,
    artifact_sha256 TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_model ON runs(model_name, created_at);
CREATE TABLE IF NOT EXISTS registry (
    model_name TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(id),
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS promotion_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES runs(id),
    accepted INTEGER NOT NULL CHECK (accepted IN (0,1)),
    reasons_json TEXT NOT NULL,
    policy_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_run ON promotion_audit(run_id, id);
