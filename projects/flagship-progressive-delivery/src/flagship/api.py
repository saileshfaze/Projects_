"""Optional local HTTP evaluator; no authentication, do not expose publicly."""
from .core import load_flags, evaluate

def create_app(config='data/flags.json'):
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    app=FastAPI(title='Flagship Lab')
    class Request(BaseModel):
        subject: str
        context: dict = {}
    @app.post('/evaluate/{flag_key}')
    def evaluate_flag(flag_key: str, request: Request):
        flags=load_flags(config)
        if flag_key not in flags: raise HTTPException(404,'Unknown flag')
        return evaluate(flags[flag_key],request.subject,request.context).__dict__
    return app
