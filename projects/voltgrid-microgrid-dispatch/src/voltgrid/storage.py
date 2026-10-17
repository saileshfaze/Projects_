"""Immutable simulation history with SQLite WAL and canonical SHA-256 inputs."""

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path

def canonical_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

class RunStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        sql = files("voltgrid").joinpath("sql/001_init.sql").read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript(sql)

    def _connect(self):
        conn = sqlite3.connect(str(self.path), timeout=10)
        conn.execute("PRAGMA busy_timeout=10000")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def save(self, run_id: str, scenario: dict, result: dict) -> None:
        serialized = canonical_json(scenario)
        digest = hashlib.sha256(serialized.encode()).hexdigest()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO dispatch_runs VALUES (?, ?, ?, ?, ?)",
                (run_id, datetime.now(timezone.utc).isoformat(), digest,
                 serialized, canonical_json(result)),
            )

    def get(self, run_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, created_at, scenario_sha256, result_json "
                "FROM dispatch_runs WHERE id = ?", (run_id,)
            ).fetchone()
        if row is None:
            return None
        return dict(run_id=row[0], created_at=row[1],
                    scenario_sha256=row[2], result=json.loads(row[3]))
