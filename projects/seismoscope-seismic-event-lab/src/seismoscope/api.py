"""Optional stateless demonstration API."""
from .pipeline import run

def create_app():
    from fastapi import FastAPI,Query
    app=FastAPI(title='SeismoScope Synthetic Event Lab',version='0.1.0')
    @app.get('/health')
    def health():return {'status':'ok'}
    @app.get('/simulate')
    def simulate(seed:int=Query(default=42,ge=0,le=1000000)):
        return run(seed)
    return app
