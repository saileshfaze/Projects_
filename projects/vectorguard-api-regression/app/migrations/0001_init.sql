PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK(version > 0),
    schema_json TEXT NOT NULL CHECK(json_valid(schema_json)),
    samples_json TEXT NOT NULL CHECK(json_valid(samples_json)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE(contract_id, version)
);
CREATE INDEX IF NOT EXISTS idx_snapshots_contract ON snapshots(contract_id, version DESC);
CREATE TABLE IF NOT EXISTS evaluations (
    id TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL,
    snapshot_version INTEGER NOT NULL,
    report_json TEXT NOT NULL CHECK(json_valid(report_json)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY(contract_id, snapshot_version) REFERENCES snapshots(contract_id, version)
);
CREATE INDEX IF NOT EXISTS idx_evaluations_contract ON evaluations(contract_id, created_at DESC);
