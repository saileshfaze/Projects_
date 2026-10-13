"""Request validation for public HTTP endpoints."""
from typing import Any

from pydantic import BaseModel, Field


class SnapshotInput(BaseModel):
    samples: list[dict[str, Any]] = Field(min_length=1, max_length=1000)


class EvaluationInput(SnapshotInput):
    version: int | None = Field(default=None, ge=1)
    lexical_limit: float = Field(default=0.55, ge=0, le=1)
    metric_path: str | None = Field(default=None, max_length=120)
    psi_limit: float = Field(default=0.2, ge=0)
    ks_limit: float = Field(default=0.3, ge=0, le=1)
