"""FastAPI facade. Importing the core planner does not require web dependencies."""
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .service import analyze

app = FastAPI(title="QueryWeaver Planner Lab", version="1.0.0",
              description="Cost-based planning for a constrained SQL dialect; synthetic datasets only.")


class PlanRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=10000)
    seed: int = Field(default=2026, ge=0, le=1000000)
    execute: bool = False
    allow_cross: bool = False


@app.get("/health")
def health():
    return {"status": "ok", "service": "queryweaver"}


@app.post("/plan")
def plan(request: PlanRequest):
    try:
        return analyze(request.sql, request.seed, request.execute, request.allow_cross)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
