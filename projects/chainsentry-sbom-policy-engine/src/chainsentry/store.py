"""SQLite append-only scan history with deterministic drift reports."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .models import Report

SCHEMA = """
CREATE TABLE IF NOT EXISTS scans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project TEXT NOT NULL,
  created_at TEXT NOT NULL,
  digest TEXT NOT NULL,
  status TEXT NOT NULL,
  report_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_scans_project_id ON scans(project,id);
"""


class ScanStore:
    def __init__(self, path: str | Path):
        self.path = str(path)
        with self._connect() as db:
            db.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def save(self, project: str, report: Report) -> int:
        if not project or len(project) > 128:
            raise ValueError("project must be 1..128 characters")
        with self._connect() as db:
            cur = db.execute("INSERT INTO scans(project,created_at,digest,status,report_json) VALUES(?,?,?,?,?)",
                             (project, datetime.now(timezone.utc).isoformat(), report.digest, report.status,
                              json.dumps(report.to_dict(), sort_keys=True)))
            return int(cur.lastrowid)

    def get(self, scan_id: int) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM scans WHERE id=?", (scan_id,)).fetchone()
        if row is None:
            return None
        return {"id": row["id"], "project": row["project"], "created_at": row["created_at"],
                "report": json.loads(row["report_json"])}

    def history(self, project: str, limit: int = 20) -> list[dict[str, Any]]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be 1..100")
        with self._connect() as db:
            rows = db.execute("SELECT id,created_at,digest,status FROM scans WHERE project=? ORDER BY id DESC LIMIT ?",
                              (project, limit)).fetchall()
        return [dict(row) for row in rows]


def diff_reports(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Compare finding identities; report severity and exemption changes separately."""
    def key(f: dict[str, Any]) -> tuple[str, str, str, str]:
        return (f["kind"], f["rule"], f["component"], f.get("advisory") or "")

    old = {key(f): f for f in before["findings"]}
    new = {key(f): f for f in after["findings"]}
    def encode(keys: set[tuple[str, ...]]) -> list[dict[str, Any]]:
        return [dict(zip(("kind", "rule", "component", "advisory"), k)) for k in sorted(keys)]
    changed = [dict(identity=dict(zip(("kind", "rule", "component", "advisory"), k)),
                    before={"severity": old[k]["severity"], "exempted": old[k]["exempted"]},
                    after={"severity": new[k]["severity"], "exempted": new[k]["exempted"]})
               for k in sorted(old.keys() & new.keys())
               if (old[k]["severity"], old[k]["exempted"]) != (new[k]["severity"], new[k]["exempted"])]
    return {"before_digest": before["digest"], "after_digest": after["digest"],
            "added": encode(new.keys() - old.keys()), "resolved": encode(old.keys() - new.keys()), "changed": changed}
