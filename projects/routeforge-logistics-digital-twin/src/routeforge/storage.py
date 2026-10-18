"""SQLite plan repository: transactional inserts and parameterized lookups."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS plans (
    plan_id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_plans_created_at ON plans(created_at);
"""

def init_db(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.executescript(SCHEMA)

def save_plan(path: str, plan: dict) -> None:
    init_db(path)
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("INSERT OR IGNORE INTO plans(plan_id,payload_json) VALUES(?,?)",
                               (plan["plan_id"], json.dumps(plan, sort_keys=True)))

def load_plan(path: str, plan_id: str) -> dict | None:
    if not Path(path).exists():
        return None
    with closing(sqlite3.connect(path)) as connection:
        row = connection.execute("SELECT payload_json FROM plans WHERE plan_id=?", (plan_id,)).fetchone()
    return json.loads(row[0]) if row else None
