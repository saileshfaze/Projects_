"""HTTP endpoints with strict Pydantic request validation."""
import os
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from .models import Thresholds
from .service import analyze
from .persistence import Store

app=FastAPI(title='SkyWeave Airspace Conflict Lab',version='0.1.0')
class FixIn(BaseModel):
    t:float
    lat:float
    lon:float
    alt_ft:float
class FlightIn(BaseModel):
    callsign:str
    fixes:list[FixIn]
class AnalyzeIn(BaseModel):
    flights:list[FlightIn]
    horizontal_nm:float=Field(default=5,gt=0)
    vertical_ft:float=Field(default=1000,gt=0)
    samples:int=Field(default=0,ge=0,le=1000)
    seed:int=42

@app.get('/health')
def health():return {'status':'ok','service':'skyweave'}

@app.post('/v1/analyze')
def analyze_request(body:AnalyzeIn):
    try:
        return analyze({'flights':[f.model_dump() for f in body.flights]},Thresholds(body.horizontal_nm,body.vertical_ft),body.samples,body.seed)
    except (ValueError,KeyError,TypeError) as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc

@app.post('/v1/runs',status_code=201)
def save_run(body:AnalyzeIn):
    scenario={'flights':[f.model_dump() for f in body.flights]}
    try:
        report=analyze(scenario,Thresholds(body.horizontal_nm,body.vertical_ft),body.samples,body.seed)
    except (ValueError,KeyError,TypeError) as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
    run_id=Store(os.environ.get('SKYWEAVE_DB','skyweave.db')).save(scenario,report)
    return {'run_id':run_id,'report':report}

@app.get('/v1/runs/{run_id}')
def get_run(run_id:str):
    result=Store(os.environ.get('SKYWEAVE_DB','skyweave.db')).load(run_id)
    if result is None:raise HTTPException(status_code=404,detail='run not found')
    return result
