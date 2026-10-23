"""FastAPI service. For demos only; add auth and quotas before exposure."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from .schemas import IngestRequest, SearchRequest, EvalRequest
from .retrieval import Document, HybridIndex
from .grounding import answer, verify_citations
from .evaluation import evaluate
from .storage import connect, ingest, all_documents, save_evaluation


def create_app(database: str | None = None) -> FastAPI:
    path = database or os.environ.get("VERITYRAG_DB", "/tmp/verityrag.db")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.db = connect(path)
        try:
            yield
        finally:
            app.state.db.close()

    app = FastAPI(title="VerityRAG Evidence Lab", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/v1/documents")
    async def documents(payload: IngestRequest, request: Request):
        docs = [Document(**d.model_dump()) for d in payload.documents]
        try:
            count = ingest(request.app.state.db, docs)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {"upserted": count}

    @app.post("/v1/search")
    async def search(payload: SearchRequest, request: Request):
        idx = HybridIndex(all_documents(request.app.state.db))
        return {"hits": [hit.as_dict() for hit in idx.search(payload.query, payload.k)]}

    @app.post("/v1/answer")
    async def extractive_answer(payload: SearchRequest, request: Request):
        docs = all_documents(request.app.state.db)
        hits = HybridIndex(docs).search(payload.query, payload.k)
        result = answer(payload.query, hits)
        if not result.abstained and not verify_citations(result, {d.id: d.body for d in docs}):
            raise HTTPException(500, "citation verification failed")
        return result.as_dict()

    @app.post("/v1/evaluate")
    async def run_eval(payload: EvalRequest, request: Request):
        idx = HybridIndex(all_documents(request.app.state.db))
        result = evaluate(idx, [q.model_dump() for q in payload.questions],
                          {k: set(v) for k, v in payload.qrels.items()}, payload.k)
        result["evaluation_id"] = save_evaluation(request.app.state.db, result)
        return result

    return app


app = create_app()
