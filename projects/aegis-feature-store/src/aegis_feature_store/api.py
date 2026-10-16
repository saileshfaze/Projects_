"""REST interface for feature registration, ingestion and serving."""

from contextlib import asynccontextmanager
from hmac import compare_digest

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from .config import Settings
from .models import (
    DriftRequest,
    FeatureView,
    IngestRequest,
    JoinRequest,
    MaterializeRequest,
)
from .quality import drift_report
from .store import FeatureStore, StoreError

REQUESTS = Counter(
    "aegis_http_requests_total", "HTTP requests handled", ["method", "route", "status"]
)
LATENCY = Histogram(
    "aegis_http_request_duration_seconds", "HTTP request duration", ["route"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings.from_env()
    app.state.settings = settings
    app.state.store = FeatureStore(settings.db_path)
    yield


app = FastAPI(
    title="Aegis Feature Store",
    version="0.1.0",
    description="Versioned feature views, leakage-safe offline joins, online snapshots.",
    lifespan=lifespan,
)


@app.middleware("http")
async def observe(request: Request, call_next):
    import time

    start = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    route_name = route.path if route is not None else "unmatched"
    REQUESTS.labels(request.method, route_name, str(response.status_code)).inc()
    LATENCY.labels(route_name).observe(time.perf_counter() - start)
    return response


@app.exception_handler(StoreError)
async def store_error_handler(request: Request, exc: StoreError):
    conflict = "Conflicting payload" in str(exc) or "already registered" in str(exc)
    return JSONResponse(status_code=409 if conflict else 422, content={"detail": str(exc)})


def get_store(request: Request) -> FeatureStore:
    return request.app.state.store


def require_key(request: Request, x_api_key: str | None = Header(default=None)):
    expected = request.app.state.settings.api_key
    if expected and (not x_api_key or not compare_digest(x_api_key, expected)):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(store: FeatureStore = Depends(get_store)):
    return {"status": "ready", **store.stats()}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/views", status_code=201, dependencies=[Depends(require_key)])
def register_view(view: FeatureView, store: FeatureStore = Depends(get_store)):
    return store.register(view)


@app.get("/v1/views", dependencies=[Depends(require_key)])
def list_views(store: FeatureStore = Depends(get_store)):
    return {"views": store.list_views()}


@app.post("/v1/events:ingest", dependencies=[Depends(require_key)])
def ingest_events(body: IngestRequest, request: Request,
                  store: FeatureStore = Depends(get_store)):
    if len(body.events) > request.app.state.settings.max_batch_size:
        raise HTTPException(status_code=413, detail="Batch exceeds configured limit")
    return store.ingest(body.view_name, body.version, body.events)


@app.post("/v1/offline:join", dependencies=[Depends(require_key)])
def offline_join(body: JoinRequest, request: Request,
                 store: FeatureStore = Depends(get_store)):
    if len(body.observations) > request.app.state.settings.max_batch_size:
        raise HTTPException(status_code=413, detail="Batch exceeds configured limit")
    return {"rows": store.offline_join(body.view_name, body.version, body.observations)}


@app.post("/v1/materializations", dependencies=[Depends(require_key)])
def materialize(body: MaterializeRequest, store: FeatureStore = Depends(get_store)):
    return store.materialize(body.view_name, body.version, body.as_of)


@app.get("/v1/online/{view_name}/{entity_key}", dependencies=[Depends(require_key)])
def online_get(view_name: str, entity_key: str, version: int = Query(ge=1),
               as_of: str | None = None, store: FeatureStore = Depends(get_store)):
    result = store.online_get(view_name, version, entity_key, as_of)
    if result is None:
        raise HTTPException(status_code=404, detail="No fresh materialized features")
    return result


@app.post("/v1/quality/drift", dependencies=[Depends(require_key)])
def quality_drift(body: DriftRequest):
    try:
        return drift_report(body.reference, body.current, body.bins)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
