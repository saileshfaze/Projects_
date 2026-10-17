"""FastAPI surface; all optimization inputs are validated Pydantic models."""

from functools import lru_cache
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .analytics import sustainability, validate_solution
from .domain import Scenario
from .forecast import seasonal_forecast
from .optimizer import OptimizationError, SolverOptions, solve
from .settings import Settings
from .storage import RunStore

app = FastAPI(
    title="VoltGrid Microgrid Dispatch",
    version="0.1.0",
    description="Scenario planning for battery, solar, energy cost and carbon.",
)

@lru_cache
def get_store() -> RunStore:
    return RunStore(Settings.from_env().database_path)

class ForecastRequest(BaseModel):
    history_kw: list[float] = Field(min_length=2)
    horizon: int = Field(ge=1, le=168)
    season_length: int = Field(ge=1)
    coverage: float = Field(gt=0, lt=1, default=0.9)

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "voltgrid"}

@app.post("/v1/forecast")
def forecast(request: ForecastRequest):
    try:
        return seasonal_forecast(
            request.history_kw, request.horizon, request.season_length, request.coverage
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/v1/dispatches", status_code=201)
def create_dispatch(scenario: Scenario, store: RunStore = Depends(get_store)):
    settings = Settings.from_env()
    try:
        result = solve(scenario, SolverOptions(
            settings.solver_time_limit_seconds, settings.solver_relative_gap
        ))
    except OptimizationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    issues = validate_solution(scenario, result)
    if issues:
        raise HTTPException(status_code=500, detail={"invariant_violations": issues})
    result["sustainability"] = sustainability(scenario, result)
    run_id = str(uuid4())
    store.save(run_id, scenario.model_dump(mode="json"), result)
    return {"run_id": run_id, "result": result}

@app.get("/v1/dispatches/{run_id}")
def get_dispatch(run_id: str, store: RunStore = Depends(get_store)):
    run = store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run
