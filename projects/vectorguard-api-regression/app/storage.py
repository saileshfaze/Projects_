"""SQLite-backed append-only contract snapshots and evaluation history."""
import json
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from .schema import infer

MIGRATION = Path(__file__).parent / "migrations" / "0001_init.sql"


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        con = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=10000")
        return con

    def init(self):
        with closing(self.connect()) as con:
            con.executescript(MIGRATION.read_text(encoding="utf-8"))

    def snapshot(self, contract_id, samples):
        inferred = infer(samples)
        with closing(self.connect()) as con:
            try:
                con.execute("BEGIN IMMEDIATE")
                row = con.execute(
                    "SELECT COALESCE(MAX(version), 0) + 1 AS version FROM snapshots WHERE contract_id=?",
                    (contract_id,),
                ).fetchone()
                version = row["version"]
                con.execute(
                    "INSERT INTO snapshots(contract_id, version, schema_json, samples_json) VALUES(?,?,?,?)",
                    (contract_id, version, json.dumps(inferred), json.dumps(samples)),
                )
                con.commit()
            except Exception:
                con.rollback()
                raise
        return {"contract_id": contract_id, "version": version, "schema": inferred}

    def get_snapshot(self, contract_id, version=None):
        sql = "SELECT * FROM snapshots WHERE contract_id=?"
        params = [contract_id]
        if version is not None:
            sql += " AND version=?"
            params.append(version)
        sql += " ORDER BY version DESC LIMIT 1"
        with closing(self.connect()) as con:
            row = con.execute(sql, params).fetchone()
        if row is None:
            return None
        return {
            "contract_id": row["contract_id"],
            "version": row["version"],
            "schema": json.loads(row["schema_json"]),
            "samples": json.loads(row["samples_json"]),
            "created_at": row["created_at"],
        }

    def versions(self, contract_id):
        with closing(self.connect()) as con:
            rows = con.execute(
                "SELECT contract_id, version, created_at FROM snapshots WHERE contract_id=? ORDER BY version DESC",
                (contract_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def record(self, contract_id, version, report):
        run_id = str(uuid.uuid4())
        with closing(self.connect()) as con:
            con.execute(
                "INSERT INTO evaluations(id, contract_id, snapshot_version, report_json) VALUES(?,?,?,?)",
                (run_id, contract_id, version, json.dumps(report)),
            )
        return run_id

    def evaluation(self, run_id):
        with closing(self.connect()) as con:
            row = con.execute("SELECT * FROM evaluations WHERE id=?", (run_id,)).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "contract_id": row["contract_id"],
            "snapshot_version": row["snapshot_version"],
            "report": json.loads(row["report_json"]),
            "created_at": row["created_at"],
        }
