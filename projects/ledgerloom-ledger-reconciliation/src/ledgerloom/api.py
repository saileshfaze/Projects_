"""Optional read-only HTTP endpoints. No authentication: local demo only."""
import os
try:
    from fastapi import FastAPI
except ImportError as exc:
    raise RuntimeError("Install optional api dependencies: pip install -e '.[api]'") from exc
from .journal import Journal
app=FastAPI(title="LedgerLoom Lab",version="0.1.0")
def db():
    return Journal(os.environ.get("LEDGERLOOM_DB","ledgerloom.sqlite3"))
@app.get("/health")
def health():
    return {"status":"ok","audit_valid":db().verify()}
@app.get("/trial-balance")
def trial_balance(through:str|None=None):
    return {"balances":db().trial_balance(through)}
@app.get("/audit/head")
def audit_head():
    return {"head":db().head()}
