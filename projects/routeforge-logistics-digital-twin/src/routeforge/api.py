"""REST interface. Demo only: add authentication before public deployment."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .baseline import compare
from .domain import parse_problem
from .optimizer import optimize
from .scenario import simulate
from .storage import load_plan, save_plan

app = FastAPI(title="RouteForge Logistics Digital Twin", version="0.1.0")

class OptimizeRequest(BaseModel):
    depot: dict
    jobs: list[dict] = Field(min_length=1, max_length=500)
    vehicles: list[dict] = Field(min_length=1, max_length=100)
    include_stress_test: bool = False

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}

@app.post("/v1/optimize")
def create_plan(request: OptimizeRequest) -> dict:
    try:
        problem = parse_problem(request.model_dump(exclude={"include_stress_test"}))
        plan = optimize(problem)
        plan["baseline"] = compare(problem, plan)
        if request.include_stress_test:
            plan["stress_test"] = simulate(problem, plan, trials=100)
        save_plan(os.getenv("ROUTEFORGE_DB", "data/routeforge.db"), plan)
        return plan
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.get("/v1/plans/{plan_id}")
def get_plan(plan_id: str) -> dict:
    plan = load_plan(os.getenv("ROUTEFORGE_DB", "data/routeforge.db"), plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
