"""Public request/response contracts."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Correction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid_from: date
    valid_to: date
    payload: dict[str, Any]
    actor: str = Field(min_length=1, max_length=128)
    idempotency_key: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def interval_is_valid(self) -> "Correction":
        if self.valid_from >= self.valid_to:
            raise ValueError("valid_from must be earlier than valid_to")
        return self


class Receipt(BaseModel):
    operation_id: str
    recorded_at: datetime
    chain_hash: str
    replayed: bool = False


class EntitySnapshot(BaseModel):
    tenant: str
    entity: str
    valid_at: date
    known_at: datetime
    payload: dict[str, Any]
    valid_from: date
    valid_to: date
    system_from: datetime
    operation_id: str


class AuditReport(BaseModel):
    tenant: str
    operations: int
    versions: int
    valid: bool
    problems: list[str]
