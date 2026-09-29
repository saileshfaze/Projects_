from fastapi import FastAPI
from prometheus_client import Counter,Histogram,make_asgi_app
from .config import get_settings
from .db import build_engine,save_decision,summary
from .risk import RiskEngine
from .schemas import Transaction,RiskDecision
settings=get_settings(); engine=build_engine(settings.database_url); risk=RiskEngine(settings.risk_threshold,settings.model_seed)
REQUESTS=Counter("sentinel_scores_total","Risk scoring requests",["decision"]); LATENCY=Histogram("sentinel_score_seconds","Risk scoring latency")
app=FastAPI(title="SentinelStream Risk API",version="0.1.0"); app.mount("/metrics",make_asgi_app())
@app.get("/health")
def health()->dict: return {"status":"ok","environment":settings.app_env}
@app.post("/v1/score",response_model=RiskDecision)
def score_transaction(tx:Transaction)->RiskDecision:
    with LATENCY.time(): result=risk.score(tx); save_decision(engine,tx,result)
    REQUESTS.labels(result.decision).inc(); return result
@app.get("/v1/analytics/summary")
def analytics_summary()->dict: return summary(engine)
