"""SQLite report registry with idempotent content-addressed runs."""
import hashlib
import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
 run_id TEXT PRIMARY KEY,
 dataset_id TEXT NOT NULL,
 report_json TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class ReportStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    def put(self, dataset_id: str, report: dict) -> str:
        canonical = json.dumps(report, sort_keys=True, separators=(",", ":"))
        run_id = hashlib.sha256((dataset_id + "\0" + canonical).encode()).hexdigest()[:24]
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO reports(run_id, dataset_id, report_json) VALUES(?,?,?)",
                         (run_id, dataset_id, canonical))
        return run_id

    def get(self, run_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT report_json FROM reports WHERE run_id=?", (run_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def list_runs(self, limit: int = 25) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT run_id, dataset_id, created_at FROM reports "
                                "ORDER BY created_at DESC, run_id LIMIT ?", (min(max(limit,1),100),)).fetchall()
        return [{"run_id": r[0], "dataset_id": r[1], "created_at": r[2]} for r in rows]
