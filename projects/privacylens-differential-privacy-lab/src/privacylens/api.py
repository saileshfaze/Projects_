"""Optional demonstration API; do not deploy publicly without authentication and durable budget controls."""
from .core import PrivacyLedger, private_histogram
import random
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError:
    FastAPI = None
if FastAPI:
    app = FastAPI(title="PrivacyLens demonstration API")
    class HistogramRequest(BaseModel):
        rows: list[dict]
        key: str
        categories: list[str]
        epsilon: float = 1.0
    @app.post("/histogram")
    def histogram(request: HistogramRequest):
        ledger = PrivacyLedger(request.epsilon)
        return {"noisy_counts": private_histogram(request.rows, request.key, request.categories,
                                                   request.epsilon, ledger, random.SystemRandom()),
                "accounting": ledger.report(),
                "warning": "Per-request budget only; no cross-request accounting"}
else:
    app = None
