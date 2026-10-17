-- Reference copy of src/voltgrid/sql/001_init.sql (the packaged migration).
CREATE TABLE IF NOT EXISTS dispatch_runs (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    scenario_sha256 TEXT NOT NULL,
    scenario_json TEXT NOT NULL,
    result_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dispatch_runs_created_at ON dispatch_runs(created_at);
