"""SQLite-backed immutable simulation runs and their audit trails."""
from __future__ import annotations
from dataclasses import asdict
import hashlib
import json
import sqlite3
from pathlib import Path
from .audit import canonical, chain, verify
from .models import Dispatch, Site, Summary

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY, created_at TEXT NOT NULL, strategy TEXT NOT NULL,
    config_json TEXT NOT NULL, summary_json TEXT NOT NULL, audit_json TEXT NOT NULL
);
"""


def init(path: str | Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)


def store(path: str | Path, site: Site, summary: Summary, steps: list[Dispatch]) -> str:
    init(path)
    from datetime import datetime, timezone
    cfg = asdict(site)
    records = chain(steps)
    signature = {"config": cfg, "summary": asdict(summary), "audit_hash": records[-1]["hash"]}
    run_id = hashlib.sha256(canonical(signature)).hexdigest()[:24]
    with sqlite3.connect(path) as conn:
        conn.execute("INSERT OR IGNORE INTO runs VALUES (?,?,?,?,?,?)", (
            run_id, datetime.now(timezone.utc).isoformat(), summary.strategy,
            json.dumps(cfg, sort_keys=True), json.dumps(asdict(summary), sort_keys=True),
            json.dumps(records, sort_keys=True)))
    return run_id


def fetch(path: str | Path, run_id: str) -> dict | None:
    init(path)
    with sqlite3.connect(path) as conn:
        row = conn.execute("SELECT id, created_at, strategy, config_json, summary_json, audit_json FROM runs WHERE id=?", (run_id,)).fetchone()
    if row is None:
        return None
    entries = json.loads(row[5])
    return {"id": row[0], "created_at": row[1], "strategy": row[2], "site": json.loads(row[3]),
            "summary": json.loads(row[4]), "audit_valid": verify(entries), "audit_head": entries[-1]["hash"]}


def list_runs(path: str | Path, limit: int = 50) -> list[dict]:
    init(path)
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT id, created_at, strategy, summary_json FROM runs ORDER BY created_at DESC LIMIT ?", (min(max(1,limit),500),)).fetchall()
    return [{"id": row[0], "created_at": row[1], "strategy": row[2], "summary": json.loads(row[3])} for row in rows]
