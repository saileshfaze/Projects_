"""Optional read-only FastAPI simulation endpoint. Not for public deployment."""
from .model import from_dict
from .solver import solve
from .scenarios import simulate

def create_app():
    from fastapi import FastAPI,HTTPException
    app=FastAPI(title='HydroGraph Synthetic Network Lab')
    @app.get('/health')
    def health():return {'status':'ok'}
    @app.post('/solve')
    def calculate(payload:dict):
        try:
            network=from_dict(payload)
            if len(network.demands)>100 or len(network.pipes)>500:raise ValueError('network too large')
            return solve(network).as_dict()
        except (ValueError,KeyError,TypeError,ArithmeticError) as exc:
            raise HTTPException(status_code=422,detail=str(exc)) from exc
    return app
