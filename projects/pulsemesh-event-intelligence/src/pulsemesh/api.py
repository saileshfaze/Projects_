"""REST API. Data access is tenant scoped; auth is optional for local demos."""
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from hmac import compare_digest

from fastapi import Depends, FastAPI, Header, HTTPException, Path, Query
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from .analytics import score_windows
from .contracts import validate_contract
from .models import BatchRequest, BatchResponse, IngestResult, WindowRow, AnomalyRow
from .settings import Settings
from .storage import EventStore

INGESTED = Counter("pulsemesh_ingest_events_total", "Events by ingestion result", ["status"])
TENANT_PATTERN = r"^[a-z][a-z0-9_-]{0,63}$"


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings.from_env()
    store = EventStore(config.database_path, config.allowed_lateness_seconds)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        store.initialize()
        app.state.store = store
        yield

    app = FastAPI(title="PulseMesh Event Intelligence", version="0.1.0", lifespan=lifespan)

    def authorize(x_api_key: str | None = Header(default=None)) -> None:
        if config.api_key and (x_api_key is None or not compare_digest(x_api_key, config.api_key)):
            raise HTTPException(status_code=401, detail="Invalid API key")

    def validate_range(start: datetime, end: datetime, window_seconds: int) -> None:
        if start.tzinfo is None or end.tzinfo is None:
            raise HTTPException(status_code=422, detail="Start and end require timezone offsets")
        if end <= start or end - start > timedelta(days=31):
            raise HTTPException(status_code=422, detail="Time range must be positive and <= 31 days")
        if not 60 <= window_seconds <= 86400:
            raise HTTPException(status_code=422, detail="window_seconds must be 60..86400")

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "0.1.0"}

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.post("/v1/tenants/{tenant}/events", response_model=BatchResponse, dependencies=[Depends(authorize)])
    def ingest(
        request: BatchRequest,
        tenant: str = Path(pattern=TENANT_PATTERN),
    ):
        if len(request.events) > config.max_batch_size:
            raise HTTPException(status_code=413, detail="Batch exceeds configured maximum")
        try:
            for event in request.events:
                validate_contract(event)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        results = []
        for event in request.events:
            try:
                status = store.ingest(tenant, event)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            INGESTED.labels(status=status).inc()
            results.append(IngestResult(event_id=event.event_id, status=status))
        return BatchResponse(
            tenant=tenant,
            accepted=sum(item.status == "accepted" for item in results),
            duplicates=sum(item.status == "duplicate" for item in results),
            late=sum(item.status == "late" for item in results),
            results=results,
        )

    @app.get("/v1/tenants/{tenant}/windows", response_model=list[WindowRow], dependencies=[Depends(authorize)])
    def windows(
        tenant: str = Path(pattern=TENANT_PATTERN),
        start: datetime = Query(),
        end: datetime = Query(),
        window_seconds: int = Query(default=3600, ge=60, le=86400),
    ):
        validate_range(start, end, window_seconds)
        return store.windows(tenant, start, end, window_seconds)

    @app.get("/v1/tenants/{tenant}/anomalies", response_model=list[AnomalyRow], dependencies=[Depends(authorize)])
    def anomalies(
        tenant: str = Path(pattern=TENANT_PATTERN),
        start: datetime = Query(),
        end: datetime = Query(),
        window_seconds: int = Query(default=3600, ge=60, le=86400),
        threshold: float = Query(default=3.5, gt=0, le=1000),
    ):
        validate_range(start, end, window_seconds)
        return score_windows(store.windows(tenant, start, end, window_seconds), threshold)

    return app


app = create_app()
