"""REST interface. Deliberately unauthenticated for local evaluation only."""

import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from atlasflow.db import Store
from atlasflow.schemas import DatasetCreate, Evaluation, PromotionPolicy, RunCreate
from atlasflow.service import DomainError, RegistryService


def create_app(database_path: str | None = None) -> FastAPI:
    app = FastAPI(title="AtlasFlow ML Orchestrator", version="0.1.0")
    path = database_path or os.environ.get("ATLAS_DB_PATH", "./var/atlasflow.sqlite3")
    app.state.service = RegistryService(Store(path))

    @app.exception_handler(DomainError)
    async def domain_error(_request: Request, error: DomainError):
        return JSONResponse({"detail": str(error)}, status_code=error.status_code)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/v1/datasets", status_code=201)
    def register_dataset(body: DatasetCreate):
        return app.state.service.register_dataset(body)

    @app.post("/v1/runs", status_code=201)
    def create_run(body: RunCreate):
        return app.state.service.create_run(body)

    @app.get("/v1/runs/{run_id}")
    def get_run(run_id: str):
        return app.state.service.get_run(run_id)

    @app.post("/v1/runs/{run_id}/evaluate")
    def evaluate(run_id: str, body: Evaluation):
        return app.state.service.evaluate(run_id, body)

    @app.post("/v1/runs/{run_id}/promote")
    def promote(run_id: str, body: PromotionPolicy):
        return app.state.service.promote(run_id, body)

    @app.get("/v1/runs/{run_id}/lineage")
    def lineage(run_id: str):
        return app.state.service.lineage(run_id)

    @app.get("/v1/runs/{run_id}/audit")
    def audit(run_id: str):
        return app.state.service.audit(run_id)

    @app.get("/v1/models/{model_name}/champion")
    def champion(model_name: str):
        return app.state.service.get_champion(model_name)

    return app


app = create_app()
