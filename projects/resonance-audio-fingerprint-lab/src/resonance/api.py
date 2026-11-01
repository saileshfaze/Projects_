"""Local REST API. Uploaded audio is bounded and never sent to third parties."""
from __future__ import annotations
import base64
import binascii
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .catalog import Catalog

class ClipRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    wav_base64: str = Field(min_length=8, max_length=32_000_000)

class SearchRequest(BaseModel):
    wav_base64: str = Field(min_length=8, max_length=32_000_000)
    limit: int = Field(default=5, ge=1, le=50)


def _decode(value: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(422, "invalid base64 WAV") from exc


def create_app(database: str | None = None) -> FastAPI:
    app = FastAPI(title="Resonance Audio Fingerprint Lab", version="0.1.0")
    db = Catalog(database or os.getenv("RESONANCE_DB", ":memory:"))
    app.state.catalog = db

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "resonance"}

    @app.get("/clips")
    def clips():
        return db.list_clips()

    @app.get("/clips/{clip_id}")
    def clip(clip_id: str):
        result = db.get(clip_id)
        if result is None:
            raise HTTPException(404, "clip not found")
        return result

    @app.post("/clips", status_code=201)
    def ingest(body: ClipRequest):
        try:
            return db.ingest(body.name, _decode(body.wav_base64))
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.delete("/clips/{clip_id}")
    def delete(clip_id: str):
        if not db.delete(clip_id):
            raise HTTPException(404, "clip not found")
        return {"deleted": clip_id}

    @app.post("/search")
    def search(body: SearchRequest):
        try:
            return {"matches": db.search(_decode(body.wav_base64), body.limit)}
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    return app

app = create_app()
