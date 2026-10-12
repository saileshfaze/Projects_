from decimal import Decimal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .core import allocate, anomaly_scores

app = FastAPI(title='NimbusLedger FinOps', version='0.1.0')

class AllocationRequest(BaseModel):
    amount: Decimal = Field(ge=0)
    weights: dict[str, Decimal]

class AnomalyRequest(BaseModel):
    daily_costs: list[float]

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/v1/allocate')
def allocation(request: AllocationRequest):
    try:
        return {'allocation': allocate(request.amount, request.weights)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post('/v1/anomalies')
def anomalies(request: AnomalyRequest):
    return {'robust_z_scores': anomaly_scores(request.daily_costs)}
