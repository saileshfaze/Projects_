"""Optional FastAPI adapter. Install with `pip install -e '.[api]'`."""
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .service import scan
from .store import ScanStore, diff_reports

app = FastAPI(title="ChainSentry SBOM Policy Engine", version="0.1.0")


class ScanRequest(BaseModel):
    project: str = Field(min_length=1, max_length=128)
    sbom: dict
    advisories: dict
    policy: dict


def store() -> ScanStore:
    return ScanStore(os.environ.get("CHAINSENTRY_DB", "./chainsentry.db"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/scans")
def create_scan(payload: ScanRequest) -> dict:
    try:
        report = scan(payload.sbom, payload.advisories, payload.policy)
        scan_id = store().save(payload.project, report)
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    return {"id": scan_id, "report": report.to_dict()}


@app.get("/v1/scans/{scan_id}")
def get_scan(scan_id: int) -> dict:
    result = store().get(scan_id)
    if result is None:
        raise HTTPException(404, detail="scan not found")
    return result


@app.get("/v1/projects/{project}/history")
def history(project: str, limit: int = 20) -> list[dict]:
    try:
        return store().history(project, limit)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc


@app.get("/v1/diff/{before_id}/{after_id}")
def diff(before_id: int, after_id: int) -> dict:
    db = store()
    before, after = db.get(before_id), db.get(after_id)
    if before is None or after is None:
        raise HTTPException(404, detail="scan not found")
    if before["project"] != after["project"]:
        raise HTTPException(422, detail="scans belong to different projects")
    return diff_reports(before["report"], after["report"])
