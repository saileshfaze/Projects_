"""Transactional experiment lifecycle, lineage and champion promotion decisions."""

import json
import uuid
from datetime import datetime, timezone

from atlasflow.db import Store
from atlasflow.schemas import DatasetCreate, Evaluation, PromotionPolicy, RunCreate


class DomainError(Exception):
    def __init__(self, message: str, status_code: int = 409):
        super().__init__(message)
        self.status_code = status_code


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _decode_run(row: dict | None) -> dict | None:
    if row is None:
        return None
    row["config"] = json.loads(row.pop("config_json"))
    row["metrics"] = json.loads(row.pop("metrics_json")) if row["metrics_json"] else None
    return row


class RegistryService:
    def __init__(self, store: Store):
        self.store = store

    def register_dataset(self, request: DatasetCreate) -> dict:
        with self.store.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM datasets WHERE sha256=?", (request.sha256,)
            ).fetchone()
            if existing:
                if existing["row_count"] != request.row_count:
                    raise DomainError("Digest already registered with a different row count")
                return dict(existing)
            record = {
                "id": str(uuid.uuid4()),
                "name": request.name,
                "sha256": request.sha256,
                "row_count": request.row_count,
                "created_at": utcnow(),
            }
            connection.execute(
                "INSERT INTO datasets (id,name,sha256,row_count,created_at) VALUES (?,?,?,?,?)",
                tuple(record.values()),
            )
            return record

    def create_run(self, request: RunCreate) -> dict:
        with self.store.transaction() as connection:
            dataset = connection.execute(
                "SELECT id FROM datasets WHERE id=?", (request.dataset_id,)
            ).fetchone()
            if dataset is None:
                raise DomainError("Unknown dataset", 404)
            if request.idempotency_key:
                existing = connection.execute(
                    "SELECT * FROM runs WHERE idempotency_key=?", (request.idempotency_key,)
                ).fetchone()
                if existing:
                    same = (
                        existing["dataset_id"] == request.dataset_id
                        and existing["model_name"] == request.model_name
                        and existing["algorithm"] == request.algorithm
                        and existing["seed"] == request.seed
                        and json.loads(existing["config_json"]) == request.config
                    )
                    if not same:
                        raise DomainError("Idempotency key reused with different payload")
                    return _decode_run(dict(existing))
            now = utcnow()
            record = {
                "id": str(uuid.uuid4()),
                "dataset_id": request.dataset_id,
                "model_name": request.model_name,
                "algorithm": request.algorithm,
                "seed": request.seed,
                "config_json": json.dumps(request.config, sort_keys=True),
                "idempotency_key": request.idempotency_key,
                "status": "registered",
                "metrics_json": None,
                "drift_psi": None,
                "artifact_sha256": None,
                "created_at": now,
                "updated_at": now,
            }
            connection.execute(
                """INSERT INTO runs (id,dataset_id,model_name,algorithm,seed,config_json,
                idempotency_key,status,metrics_json,drift_psi,artifact_sha256,created_at,updated_at)
                VALUES (:id,:dataset_id,:model_name,:algorithm,:seed,:config_json,
                :idempotency_key,:status,:metrics_json,:drift_psi,:artifact_sha256,
                :created_at,:updated_at)""",
                record,
            )
            return _decode_run(record)

    def evaluate(self, run_id: str, request: Evaluation) -> dict:
        with self.store.transaction() as connection:
            row = connection.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if row is None:
                raise DomainError("Unknown run", 404)
            if row["status"] != "registered":
                raise DomainError("A run can be evaluated exactly once")
            metrics = request.model_dump(include={"accuracy", "precision", "recall", "f1"})
            connection.execute(
                """UPDATE runs SET status='evaluated',metrics_json=?,drift_psi=?,
                artifact_sha256=?,updated_at=? WHERE id=?""",
                (json.dumps(metrics, sort_keys=True), request.drift_psi,
                 request.artifact_sha256, utcnow(), run_id),
            )
        return self.get_run(run_id)

    def promote(self, run_id: str, policy: PromotionPolicy) -> dict:
        with self.store.transaction() as connection:
            row = connection.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
            if row is None:
                raise DomainError("Unknown run", 404)
            if row["status"] != "evaluated":
                raise DomainError("Only evaluated runs may be promoted")
            metrics = json.loads(row["metrics_json"])
            reasons = []
            if metrics["accuracy"] < policy.min_accuracy:
                reasons.append("accuracy_below_minimum")
            if metrics["f1"] < policy.min_f1:
                reasons.append("f1_below_minimum")
            if row["drift_psi"] > policy.max_drift_psi:
                reasons.append("drift_exceeds_limit")
            champion = connection.execute(
                "SELECT r.* FROM registry g JOIN runs r ON g.run_id=r.id WHERE g.model_name=?",
                (row["model_name"],),
            ).fetchone()
            if champion and not policy.allow_regression:
                champion_f1 = json.loads(champion["metrics_json"])["f1"]
                if metrics["f1"] < champion_f1:
                    reasons.append("f1_regression_against_champion")
            accepted = not reasons
            now = utcnow()
            connection.execute(
                """INSERT INTO promotion_audit
                (run_id,accepted,reasons_json,policy_json,created_at) VALUES (?,?,?,?,?)""",
                (run_id, int(accepted), json.dumps(reasons),
                 policy.model_dump_json(), now),
            )
            if accepted:
                if champion:
                    connection.execute(
                        "UPDATE runs SET status='archived',updated_at=? WHERE id=?",
                        (now, champion["id"]),
                    )
                connection.execute(
                    "UPDATE runs SET status='promoted',updated_at=? WHERE id=?",
                    (now, run_id),
                )
                connection.execute(
                    """INSERT INTO registry (model_name,run_id,updated_at) VALUES (?,?,?)
                    ON CONFLICT(model_name) DO UPDATE SET run_id=excluded.run_id,
                    updated_at=excluded.updated_at""",
                    (row["model_name"], run_id, now),
                )
            else:
                connection.execute(
                    "UPDATE runs SET status='rejected',updated_at=? WHERE id=?",
                    (now, run_id),
                )
            return {"accepted": accepted, "reasons": reasons, "run_id": run_id,
                    "champion_run_id": run_id if accepted else champion["id"] if champion else None}

    def get_run(self, run_id: str) -> dict:
        row = self.store.fetch_one("SELECT * FROM runs WHERE id=?", (run_id,))
        if row is None:
            raise DomainError("Unknown run", 404)
        return _decode_run(row)

    def get_champion(self, model_name: str) -> dict:
        row = self.store.fetch_one(
            """SELECT r.* FROM registry g JOIN runs r ON g.run_id=r.id
            WHERE g.model_name=?""", (model_name,)
        )
        if row is None:
            raise DomainError("Unknown model", 404)
        return _decode_run(row)

    def lineage(self, run_id: str) -> dict:
        run = self.get_run(run_id)
        dataset = self.store.fetch_one(
            "SELECT * FROM datasets WHERE id=?", (run["dataset_id"],)
        )
        return {"run": run, "dataset": dataset}

    def audit(self, run_id: str) -> list[dict]:
        self.get_run(run_id)
        entries = self.store.fetch_all(
            "SELECT * FROM promotion_audit WHERE run_id=? ORDER BY id", (run_id,)
        )
        for entry in entries:
            entry["reasons"] = json.loads(entry.pop("reasons_json"))
            entry["policy"] = json.loads(entry.pop("policy_json"))
            entry["accepted"] = bool(entry["accepted"])
        return entries
