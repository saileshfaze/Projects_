"""FastAPI interface; intentionally unauthenticated reference service."""

import os
from datetime import date, datetime
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query

from .audit import verify
from .models import AuditReport, Correction, EntitySnapshot, Receipt
from .service import IdempotencyConflict, Ledger, SnapshotNotFound

app = FastAPI(title="Chronos Bitemporal Ledger", version="0.1.0")


@lru_cache(maxsize=1)
def get_ledger() -> Ledger:
    return Ledger(os.getenv("CHRONOS_DB", "./chronos.sqlite3"))


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/tenants/{tenant}/entities/{entity}/corrections", response_model=Receipt)
def correct(tenant: str, entity: str, change: Correction) -> Receipt:
    try:
        return get_ledger().correct(tenant, entity, change)
    except IdempotencyConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/v1/tenants/{tenant}/entities/{entity}", response_model=EntitySnapshot)
def snapshot(
    tenant: str, entity: str, valid_at: date = Query(...),
    known_at: datetime | None = Query(default=None),
) -> EntitySnapshot:
    try:
        return get_ledger().snapshot(tenant, entity, valid_at, known_at)
    except SnapshotNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/tenants/{tenant}/entities/{entity}/history")
def history(tenant: str, entity: str) -> list[dict]:
    return get_ledger().history(tenant, entity)


@app.get("/v1/tenants/{tenant}/audit", response_model=AuditReport)
def audit(tenant: str) -> AuditReport:
    return verify(get_ledger().path, tenant)
