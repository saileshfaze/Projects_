"""FastAPI application factory. Local demonstration only; no authentication."""
import os
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from .models import Reading,QualitySpec
from .service import QualityService
class SpecIn(BaseModel):
    metric:str; lsl:float; usl:float; target:float; unit:str=''
class ReadingIn(BaseModel):
    event_id:str; timestamp:str; line:str; machine:str; metric:str; lot:str; value:float
class BatchIn(BaseModel):
    readings:list[ReadingIn]=Field(min_length=1,max_length=10000)

def create_app(db_path:str|None=None)->FastAPI:
    service=QualityService(db_path or os.getenv('METRIFORGE_DB','state/metriforge.sqlite'))
    app=FastAPI(title='MetriForge Manufacturing Quality Lab',version='0.1.0')
    @app.get('/health')
    def health(): return {'status':'ok'}
    @app.put('/specs/{metric}')
    def spec(metric:str,data:SpecIn):
        if metric!=data.metric: raise HTTPException(422,'metric path mismatch')
        try: service.set_spec(QualitySpec(**data.model_dump()))
        except ValueError as e: raise HTTPException(422,str(e)) from e
        return {'metric':metric,'status':'stored'}
    @app.post('/readings')
    def readings(data:BatchIn):
        try: return service.ingest([Reading(**r.model_dump()) for r in data.readings])
        except ValueError as e: raise HTTPException(409,str(e)) from e
    @app.get('/reports/{line}/{machine}/{metric}')
    def report(line:str,machine:str,metric:str,baseline_lot:str='baseline'):
        try: return service.report(line,machine,metric,baseline_lot)
        except ValueError as e: raise HTTPException(422,str(e)) from e
    @app.get('/audit')
    def audit(): return service.audit()
    return app
app=create_app()
