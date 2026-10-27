"""FastAPI adapter. API calls are stateless except persisted run records."""
import os
from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .models import Battery, Interval, Site
from .dispatch import simulate, compare
from .storage import store, fetch, list_runs

app=FastAPI(title="VoltPilot Microgrid Dispatch",version="0.1.0")


class IntervalIn(BaseModel):
    timestamp: str
    load_kw: float = Field(ge=0)
    pv_kw: float = Field(ge=0)
    import_eur_per_kwh: float = Field(ge=0)
    export_eur_per_kwh: float = Field(ge=0)
    carbon_kg_per_kwh: float = Field(ge=0)
    grid_available: bool = True


class SimulateIn(BaseModel):
    intervals: list[IntervalIn] = Field(min_length=1, max_length=3000)
    strategy: str = "price_aware"
    step_minutes: int = 15
    battery: dict = Field(default_factory=dict)
    site: dict = Field(default_factory=dict)


def _parse(body: SimulateIn):
    try:
        battery=Battery(**body.battery)
        site=Site(battery=battery,**body.site)
        rows=[Interval(**x.model_dump()) for x in body.intervals]
        return site,rows
    except (TypeError,ValueError) as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status":"ok","service":"voltpilot"}


@app.post("/simulate")
def run(body: SimulateIn):
    site,rows=_parse(body)
    try:
        summary,steps=simulate(rows,site,body.strategy,body.step_minutes)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
    run_id=store(os.getenv("VOLTPILOT_DB","voltpilot.db"),site,summary,steps)
    return {"id":run_id,"summary":asdict(summary),"intervals":[asdict(x) for x in steps]}


@app.post("/compare")
def comparisons(body: SimulateIn):
    site,rows=_parse(body)
    try:
        return compare(rows,site,body.step_minutes)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc


@app.get("/runs")
def runs():
    return list_runs(os.getenv("VOLTPILOT_DB","voltpilot.db"))


@app.get("/runs/{run_id}")
def run_detail(run_id: str):
    item=fetch(os.getenv("VOLTPILOT_DB","voltpilot.db"),run_id)
    if item is None:
        raise HTTPException(status_code=404,detail="run not found")
    return item
