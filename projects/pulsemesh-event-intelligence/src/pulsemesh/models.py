"""Strict, versioned input contracts for the public ingestion API."""
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    event_type: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    occurred_at: datetime
    value: float = Field(default=1.0, allow_inf_nan=False)
    attributes: dict[str, Any] = Field(default_factory=dict)
    schema_version: int = Field(default=1, ge=1, le=100)

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must contain a timezone offset")
        return value.astimezone(timezone.utc)


class BatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    events: list[Event] = Field(min_length=1, max_length=5000)


class IngestResult(BaseModel):
    event_id: str
    status: str


class BatchResponse(BaseModel):
    tenant: str
    accepted: int
    duplicates: int
    late: int
    results: list[IngestResult]


class WindowRow(BaseModel):
    bucket_start: datetime
    event_type: str
    count: int
    total_value: float


class AnomalyRow(WindowRow):
    score: float
    anomalous: bool
