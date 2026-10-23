"""External request/response contracts."""
from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    id: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=50000)
    source: str = Field(default="synthetic", max_length=200)
    category: str = Field(default="general", max_length=80)


class IngestRequest(BaseModel):
    documents: list[DocumentIn] = Field(min_length=1, max_length=1000)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    k: int = Field(default=5, ge=1, le=100)


class EvalQuestion(BaseModel):
    id: str
    question: str
    slice: str = "general"


class EvalRequest(BaseModel):
    questions: list[EvalQuestion] = Field(min_length=1, max_length=1000)
    qrels: dict[str, list[str]]
    k: int = Field(default=5, ge=1, le=100)
