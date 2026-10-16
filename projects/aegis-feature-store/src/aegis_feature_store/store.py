"""Transactional feature registry, offline joins and online materialization."""

from datetime import timedelta
import json
import sqlite3

from .db import Database
from .models import FeatureEvent, FeatureView, Observation
from .timeutils import now_utc, parse_utc, utc_text


class StoreError(ValueError):
    """Invalid input, conflicting data, or missing feature definitions."""


def _validate_values(fields: dict[str, str], values: dict[str, object]) -> None:
    if set(fields) != set(values):
        raise StoreError("Feature values must match the registered field names exactly")
    for name, expected in fields.items():
        value = values[name]
        correct = {
            "integer": type(value) is int,
            "number": type(value) in (int, float) and type(value) is not bool,
            "string": type(value) is str,
            "boolean": type(value) is bool,
        }[expected]
        if not correct:
            raise StoreError("Incorrect type for feature: " + name)
        if expected == "number":
            from math import isfinite

            if not isfinite(value):
                raise StoreError("Non-finite numerical feature: " + name)


class FeatureStore:
    def __init__(self, path: str):
        self.db = Database(path)
        self.db.migrate()

    def register(self, view: FeatureView) -> dict:
        with self.db.connect() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                conn.execute(
                    """INSERT INTO feature_views
                       (name, version, fields_json, ttl_seconds, description, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        view.name, view.version, json.dumps(view.fields, sort_keys=True),
                        view.ttl_seconds, view.description, now_utc(),
                    ),
                )
                conn.execute(
                    "INSERT INTO audit_log(operation, subject, detail_json, created_at) VALUES(?,?,?,?)",
                    ("register", view.name, json.dumps({"version": view.version}), now_utc()),
                )
                conn.commit()
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                raise StoreError("Feature view version already registered") from exc
        return view.model_dump()

    def get_view(self, name: str, version: int) -> dict:
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM feature_views WHERE name=? AND version=?", (name, version)
            ).fetchone()
        if row is None:
            raise StoreError("Unknown feature view/version")
        return {
            "name": row["name"], "version": row["version"],
            "fields": json.loads(row["fields_json"]),
            "ttl_seconds": row["ttl_seconds"], "description": row["description"],
        }

    def list_views(self) -> list[dict]:
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT name, version FROM feature_views ORDER BY name, version"
            ).fetchall()
        return [self.get_view(row["name"], row["version"]) for row in rows]

    def ingest(self, name: str, version: int, events: list[FeatureEvent]) -> dict:
        view = self.get_view(name, version)
        prepared = []
        for event in events:
            _validate_values(view["fields"], event.values)
            event_ts, available_ts = parse_utc(event.event_ts), parse_utc(event.available_ts)
            if available_ts < event_ts:
                raise StoreError("available_ts cannot precede event_ts")
            prepared.append((
                event.event_id, name, version, event.entity_key,
                utc_text(event_ts), utc_text(available_ts),
                json.dumps(event.values, sort_keys=True, allow_nan=False),
            ))
        inserted, duplicates = 0, 0
        with self.db.connect() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                for values in prepared:
                    old = conn.execute(
                        """SELECT event_id, view_name, version, entity_key,
                                  event_ts, available_ts, values_json
                           FROM feature_events WHERE event_id=?""", (values[0],)
                    ).fetchone()
                    if old is not None:
                        if tuple(old) != values:
                            raise StoreError("Conflicting payload for event_id " + values[0])
                        duplicates += 1
                        continue
                    conn.execute(
                        """INSERT INTO feature_events
                           (event_id, view_name, version, entity_key, event_ts,
                            available_ts, values_json, ingested_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (*values, now_utc())
                    )
                    inserted += 1
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return {"inserted": inserted, "duplicates": duplicates}

    def _historical(self, conn, name: str, version: int, entity: str,
                    as_of: str, ttl_seconds: int):
        cutoff = utc_text(parse_utc(as_of) - timedelta(seconds=ttl_seconds))
        return conn.execute(
            """SELECT event_id, event_ts, available_ts, values_json
               FROM feature_events
               WHERE view_name=? AND version=? AND entity_key=?
                 AND event_ts<=? AND available_ts<=? AND event_ts>=?
               ORDER BY event_ts DESC, available_ts DESC, event_id DESC
               LIMIT 1""",
            (name, version, entity, as_of, as_of, cutoff),
        ).fetchone()

    def offline_join(self, name: str, version: int,
                     observations: list[Observation]) -> list[dict]:
        view = self.get_view(name, version)
        result = []
        with self.db.connect() as conn:
            for obs in observations:
                as_of = utc_text(obs.as_of)
                row = self._historical(
                    conn, name, version, obs.entity_key, as_of, view["ttl_seconds"]
                )
                result.append({
                    "entity_key": obs.entity_key, "as_of": as_of,
                    "event_id": row["event_id"] if row else None,
                    "event_ts": row["event_ts"] if row else None,
                    "features": json.loads(row["values_json"]) if row else None,
                })
        return result

    def materialize(self, name: str, version: int, as_of: str) -> dict:
        view = self.get_view(name, version)
        snapshot = utc_text(as_of)
        cutoff = utc_text(parse_utc(snapshot) - timedelta(seconds=view["ttl_seconds"]))
        with self.db.connect() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                rows = conn.execute(
                    """SELECT entity_key, event_id, event_ts, available_ts, values_json
                       FROM (
                           SELECT entity_key, event_id, event_ts, available_ts, values_json,
                                  ROW_NUMBER() OVER (
                                    PARTITION BY entity_key
                                    ORDER BY event_ts DESC, available_ts DESC, event_id DESC
                                  ) AS rank
                           FROM feature_events
                           WHERE view_name=? AND version=?
                             AND event_ts<=? AND available_ts<=? AND event_ts>=?
                       ) WHERE rank=1""",
                    (name, version, snapshot, snapshot, cutoff),
                ).fetchall()
                conn.execute(
                    "DELETE FROM online_features WHERE view_name=? AND version=?", (name, version)
                )
                for row in rows:
                    conn.execute(
                        """INSERT INTO online_features
                           (view_name, version, entity_key, event_id, event_ts,
                            available_ts, values_json, materialized_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (name, version, row["entity_key"], row["event_id"], row["event_ts"],
                         row["available_ts"], row["values_json"], snapshot),
                    )
                conn.execute(
                    """INSERT INTO materialization_runs
                       (view_name, version, as_of, row_count, completed_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (name, version, snapshot, len(rows), now_utc()),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return {"view_name": name, "version": version, "as_of": snapshot,
                "materialized_entities": len(rows)}

    def online_get(self, name: str, version: int, entity: str, as_of: str | None = None):
        view = self.get_view(name, version)
        now = utc_text(as_of or now_utc())
        cutoff = utc_text(parse_utc(now) - timedelta(seconds=view["ttl_seconds"]))
        with self.db.connect() as conn:
            row = conn.execute(
                """SELECT event_id, event_ts, available_ts, values_json, materialized_at
                   FROM online_features
                   WHERE view_name=? AND version=? AND entity_key=?""",
                (name, version, entity),
            ).fetchone()
        if not row or not (cutoff <= row["event_ts"] <= now) or row["available_ts"] > now:
            return None
        if row["materialized_at"] > now:
            return None
        return {"event_id": row["event_id"], "event_ts": row["event_ts"],
                "features": json.loads(row["values_json"]),
                "materialized_at": row["materialized_at"]}

    def stats(self) -> dict:
        with self.db.connect() as conn:
            views = conn.execute("SELECT COUNT(*) FROM feature_views").fetchone()[0]
            events = conn.execute("SELECT COUNT(*) FROM feature_events").fetchone()[0]
            online = conn.execute("SELECT COUNT(*) FROM online_features").fetchone()[0]
            runs = conn.execute("SELECT COUNT(*) FROM materialization_runs").fetchone()[0]
        return {"registered_views": views, "ingested_events": events,
                "online_entities": online, "materialization_runs": runs}
