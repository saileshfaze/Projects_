"""Validated public request contracts."""

from typing import Annotated

from pydantic import BaseModel, Field


Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Score = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sha256: Digest
    row_count: int = Field(ge=0)


class RunCreate(BaseModel):
    dataset_id: str
    model_name: str = Field(pattern=r"^[a-zA-Z][a-zA-Z0-9_-]{1,63}$")
    algorithm: str = Field(min_length=2, max_length=80)
    seed: int = Field(ge=0, le=2**31 - 1)
    config: dict[str, str | int | float | bool] = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=128)


class Evaluation(BaseModel):
    accuracy: Score
    precision: Score
    recall: Score
    f1: Score
    drift_psi: float = Field(ge=0, allow_inf_nan=False)
    artifact_sha256: Digest | None = None


class PromotionPolicy(BaseModel):
    min_accuracy: Score = 0.75
    min_f1: Score = 0.75
    max_drift_psi: float = Field(default=0.30, ge=0, allow_inf_nan=False)
    allow_regression: bool = False
