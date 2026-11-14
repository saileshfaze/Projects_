"""Optional FastAPI service; install the api extra."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .analysis import analyze

app = FastAPI(title="HelixBench Synthetic Sequence Lab", version="0.1.0")

class SequenceRequest(BaseModel):
    sequence: str = Field(min_length=1, max_length=100000)
    k: int = Field(default=3, ge=1, le=20)
    motif: str = "ATG"
    min_codons: int = Field(default=2, ge=2)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze_sequence(request: SequenceRequest):
    try:
        return analyze(request.sequence, request.k, request.motif, request.min_codons)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
