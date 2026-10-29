"""Small FastAPI adapter over the deterministic simulation engine."""
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .raft import Cluster
from .metrics import evaluate


class TickRequest(BaseModel):
    steps: int = Field(default=1, ge=1, le=1000)


class CommandRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=128)
    op: str
    key: str = Field(min_length=1, max_length=128)
    value: int | str | None = None


class FaultRequest(BaseModel):
    kind: str
    node: str | None = None
    a: list[str] = Field(default_factory=list)
    b: list[str] = Field(default_factory=list)


def create_app(cluster: Cluster | None = None) -> FastAPI:
    app = FastAPI(title="QuorumCraft Raft Fault Lab", version="0.1.0")
    simulation = cluster if cluster is not None else Cluster()

    @app.get("/health")
    def health():
        return {"status": "ok", "simulation": True}

    @app.get("/cluster")
    def status():
        return simulation.summary()

    @app.post("/tick")
    def tick(body: TickRequest):
        simulation.tick(body.steps)
        return simulation.summary()

    @app.post("/commands")
    def command(body: CommandRequest):
        try:
            payload = {"op": body.op, "key": body.key}
            if body.op != "delete":
                payload["value"] = body.value
            index = simulation.submit(payload, body.request_id)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if index is None:
            raise HTTPException(status_code=503, detail="no elected leader")
        return {"accepted": True, "index": index, "committed": False}

    @app.post("/faults")
    def fault(body: FaultRequest):
        try:
            if body.kind == "partition":
                simulation.partition(body.a, body.b)
            elif body.kind == "heal":
                simulation.heal()
            elif body.kind in {"crash", "recover"} and body.node:
                if body.kind == "crash":
                    simulation.crash(body.node)
                else:
                    simulation.recover(body.node)
            else:
                raise ValueError("invalid fault request")
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return simulation.summary()

    @app.get("/metrics")
    def metrics():
        return evaluate(simulation)

    @app.get("/audit")
    def audit():
        return {"valid": simulation.audit.verify(), "records": simulation.audit.records}

    return app


app = create_app()
