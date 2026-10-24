"""SQLite storage with immutable assignments and idempotent events."""
from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from .assignment import arm
from .models import Experiment, Outcome

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS experiments (
 experiment_id TEXT PRIMARY KEY, config_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assignments (
 experiment_id TEXT NOT NULL, subject_id TEXT NOT NULL, arm TEXT NOT NULL CHECK(arm IN ('A','B')),
 PRIMARY KEY(experiment_id,subject_id),
 FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
);
CREATE TABLE IF NOT EXISTS outcomes (
 event_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL, subject_id TEXT NOT NULL,
 revenue REAL NOT NULL CHECK(revenue>=0), preperiod_revenue REAL NOT NULL CHECK(preperiod_revenue>=0),
 converted INTEGER NOT NULL, refunded INTEGER NOT NULL, timestamp TEXT NOT NULL,
 FOREIGN KEY(experiment_id,subject_id) REFERENCES assignments(experiment_id,subject_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS one_outcome_per_subject ON outcomes(experiment_id,subject_id);
CREATE INDEX IF NOT EXISTS outcomes_experiment ON outcomes(experiment_id);
"""


class Ledger:
    def __init__(self, path: str | Path):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=10000")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def register(self, config: Experiment) -> None:
        from dataclasses import asdict
        payload = json.dumps(asdict(config), sort_keys=True)
        with self.connect() as db:
            existing = db.execute("SELECT config_json FROM experiments WHERE experiment_id=?", (config.experiment_id,)).fetchone()
            if existing and existing[0] != payload:
                raise ValueError("experiment configuration is immutable")
            db.execute("INSERT OR IGNORE INTO experiments VALUES (?,?)", (config.experiment_id, payload))

    def config(self, experiment_id: str) -> Experiment:
        with self.connect() as db:
            row = db.execute("SELECT config_json FROM experiments WHERE experiment_id=?", (experiment_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown experiment {experiment_id}")
        return Experiment(**json.loads(row[0]))

    def assign(self, experiment_id: str, subject_id: str) -> str:
        config = self.config(experiment_id)
        result = arm(config, subject_id)
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO assignments VALUES (?,?,?)", (experiment_id, subject_id, result))
            existing = db.execute("SELECT arm FROM assignments WHERE experiment_id=? AND subject_id=?", (experiment_id, subject_id)).fetchone()[0]
        return existing

    def ingest(self, event: Outcome) -> bool:
        expected = self.assign(event.experiment_id, event.subject_id)
        del expected
        with self.connect() as db:
            existing = db.execute("SELECT * FROM outcomes WHERE event_id=?", (event.event_id,)).fetchone()
            if existing:
                fields = ("experiment_id", "subject_id", "revenue", "preperiod_revenue", "converted", "refunded", "timestamp")
                values = (event.experiment_id, event.subject_id, event.revenue, event.preperiod_revenue, int(event.converted), int(event.refunded), event.timestamp)
                if any(existing[field] != value for field, value in zip(fields, values)):
                    raise ValueError("event_id collision with different payload")
                return False
            try:
                db.execute("INSERT INTO outcomes VALUES (?,?,?,?,?,?,?,?)", (
                    event.event_id, event.experiment_id, event.subject_id, event.revenue,
                    event.preperiod_revenue, int(event.converted), int(event.refunded), event.timestamp))
            except sqlite3.IntegrityError as exc:
                raise ValueError("one outcome per subject; duplicate subject or event") from exc
            return True

    def rows(self, experiment_id: str) -> list[dict]:
        self.config(experiment_id)
        with self.connect() as db:
            return [dict(row) for row in db.execute("""
                SELECT a.arm, o.subject_id, o.revenue, o.preperiod_revenue, o.converted, o.refunded
                FROM outcomes o JOIN assignments a USING(experiment_id,subject_id)
                WHERE o.experiment_id=? ORDER BY o.subject_id
            """, (experiment_id,))]

    def counts(self, experiment_id: str) -> dict[str, int]:
        self.config(experiment_id)
        with self.connect() as db:
            counts = dict(db.execute("SELECT arm, COUNT(*) FROM assignments WHERE experiment_id=? GROUP BY arm", (experiment_id,)).fetchall())
        return {"A": counts.get("A", 0), "B": counts.get("B", 0)}
