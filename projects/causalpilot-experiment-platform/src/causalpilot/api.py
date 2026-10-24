"""Optional FastAPI adapter; install causalpilot[api] to serve."""
import os
from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .models import Experiment, Outcome
from .service import ExperimentService

app = FastAPI(title="CausalPilot Experiment Analytics", version="0.1.0")


def service() -> ExperimentService:
    return ExperimentService(os.getenv("CAUSALPILOT_DB","/tmp/causalpilot.sqlite3"))


class ExperimentPayload(BaseModel):
    experiment_id: str
    salt: str
    treatment_fraction: float = 0.5
    alpha: float = 0.05
    planned_looks: int = 1
    minimum_per_arm: int = 20


class OutcomePayload(BaseModel):
    event_id: str
    experiment_id: str
    subject_id: str
    revenue: float = Field(ge=0)
    preperiod_revenue: float = Field(ge=0)
    converted: bool
    refunded: bool
    timestamp: str


@app.get("/health")
def health():
    return {"status":"ok"}


@app.post("/experiments",status_code=201)
def register(payload: ExperimentPayload):
    try:
        config=Experiment(**payload.model_dump())
        service().register(config)
        return {"experiment_id":config.experiment_id}
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc


@app.get("/experiments/{experiment_id}/assign/{subject_id}")
def assign(experiment_id: str,subject_id: str):
    try:
        return {"arm":service().assign(experiment_id,subject_id)}
    except KeyError as exc:
        raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc


@app.post("/outcomes",status_code=201)
def outcome(payload: OutcomePayload):
    try:
        return {"created":service().ingest(Outcome(**payload.model_dump()))}
    except KeyError as exc:
        raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc


@app.get("/experiments/{experiment_id}/report")
def report(experiment_id: str):
    try:
        return service().report(experiment_id)
    except KeyError as exc:
        raise HTTPException(404,str(exc)) from exc
