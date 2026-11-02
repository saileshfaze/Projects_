"""Optional FastAPI read-only operations plus explicit snapshot/restore endpoints."""
from pathlib import Path
from .engine import Vault
from .errors import VaultlineError

def create_app(vault_dir=".vaultline"):
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
    except ImportError as exc:
        raise RuntimeError("Install vaultline[api] to enable FastAPI") from exc
    app = FastAPI(title="Vaultline Backup Lab", version="0.1.0")
    vault = Vault(vault_dir)
    class SnapshotRequest(BaseModel):
        source: str
        label: str = ""
    class RestoreRequest(BaseModel):
        target: str
        overwrite: bool = False
    def run(fn, *args):
        try: return fn(*args)
        except (VaultlineError, ValueError) as exc: raise HTTPException(400, str(exc)) from exc
    @app.get("/health")
    def health(): return {"status": "ok"}
    @app.get("/snapshots")
    def snapshots(): return run(vault.list_snapshots)
    @app.get("/stats")
    def stats(): return run(vault.stats)
    @app.post("/snapshots")
    def snapshot(req: SnapshotRequest): return run(vault.snapshot, req.source, req.label)
    @app.get("/snapshots/{identifier}/verify")
    def verify(identifier: str): return run(vault.verify, identifier)
    @app.post("/snapshots/{identifier}/restore")
    def restore(identifier: str, req: RestoreRequest): return run(vault.restore, identifier, req.target, req.overwrite)
    return app

app = None  # Use `uvicorn vaultline.server:app` for configured deployment.
