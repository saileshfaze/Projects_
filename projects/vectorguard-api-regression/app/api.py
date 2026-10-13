"""Contract registry and regression evaluation API."""
import hmac
import os
import re
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status

from .core import evaluate_samples
from .drift import drift_summary
from .models import EvaluationInput, SnapshotInput
from .storage import Store

app = FastAPI(
    title="VectorGuard Semantic API Regression",
    version="0.2.0",
    description="Versioned response contracts, compatibility gates, and offline drift analysis.",
)


def get_store():
    store = Store(os.getenv("VECTORGUARD_DB", "./vectorguard.db"))
    store.init()
    return store


def require_api_key(x_api_key: Annotated[str | None, Header()] = None):
    expected = os.getenv("VECTORGUARD_API_KEY")
    if expected and not hmac.compare_digest(expected, x_api_key or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def validate_id(contract_id):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{2,63}", contract_id):
        raise HTTPException(status_code=422, detail="Use a lowercase slug of 3-64 characters")


def metric_values(samples, path):
    parts = path.split(".")
    result = []
    for sample in samples:
        value = sample
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                raise ValueError(f"Metric path not present: {path}")
            value = value[part]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Metric path must contain numbers: {path}")
        result.append(float(value))
    return result


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(store: Store = Depends(get_store)):
    with store.connect() as con:
        con.execute("SELECT 1")
    return {"status": "ready"}


@app.post(
    "/v1/contracts/{contract_id}/snapshots",
    status_code=201,
    dependencies=[Depends(require_api_key)],
)
def create_snapshot(contract_id: str, body: SnapshotInput, store: Store = Depends(get_store)):
    validate_id(contract_id)
    return store.snapshot(contract_id, body.samples)


@app.get("/v1/contracts/{contract_id}/snapshots")
def list_snapshots(contract_id: str, store: Store = Depends(get_store)):
    validate_id(contract_id)
    return {"snapshots": store.versions(contract_id)}


@app.post(
    "/v1/contracts/{contract_id}/evaluate",
    status_code=201,
    dependencies=[Depends(require_api_key)],
)
def evaluate(contract_id: str, body: EvaluationInput, store: Store = Depends(get_store)):
    validate_id(contract_id)
    baseline = store.get_snapshot(contract_id, body.version)
    if baseline is None:
        raise HTTPException(status_code=404, detail="Baseline snapshot not found")
    report = evaluate_samples(baseline["samples"], body.samples, lexical_limit=body.lexical_limit)
    if body.metric_path:
        try:
            old = metric_values(baseline["samples"], body.metric_path)
            new = metric_values(body.samples, body.metric_path)
            report["metric_drift"] = drift_summary(
                old, new, psi_limit=body.psi_limit, ks_limit=body.ks_limit
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if report["metric_drift"]["drift_detected"]:
            report["verdict"] = "fail"
    run_id = store.record(contract_id, baseline["version"], report)
    return {"evaluation_id": run_id, "contract_id": contract_id, "version": baseline["version"], **report}


@app.get("/v1/evaluations/{evaluation_id}")
def read_evaluation(evaluation_id: str, store: Store = Depends(get_store)):
    record = store.evaluation(evaluation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return record
