"""Validated API and domain contracts."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

FeatureType = Literal["integer", "number", "string", "boolean"]


class FeatureView(BaseModel):
    name: str = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    version: int = Field(ge=1)
    fields: dict[str, FeatureType] = Field(min_length=1)
    ttl_seconds: int = Field(gt=0, le=31_536_000)
    description: str = Field(default="", max_length=500)

    @field_validator("fields")
    @classmethod
    def validate_field_names(cls, fields: dict[str, FeatureType]) -> dict[str, FeatureType]:
        import re

        if len(fields) > 100:
            raise ValueError("At most 100 fields are allowed")
        if any(not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", key) for key in fields):
            raise ValueError("Field names must be lowercase snake_case")
        return fields


class FeatureEvent(BaseModel):
    event_id: str = Field(min_length=1, max_length=128)
    entity_key: str = Field(min_length=1, max_length=256)
    event_ts: str
    available_ts: str
    values: dict[str, object]


class IngestRequest(BaseModel):
    view_name: str
    version: int = Field(ge=1)
    events: list[FeatureEvent] = Field(min_length=1)


class Observation(BaseModel):
    entity_key: str = Field(min_length=1)
    as_of: str


class JoinRequest(BaseModel):
    view_name: str
    version: int = Field(ge=1)
    observations: list[Observation] = Field(min_length=1)


class MaterializeRequest(BaseModel):
    view_name: str
    version: int = Field(ge=1)
    as_of: str


class DriftRequest(BaseModel):
    reference: list[float] = Field(min_length=2)
    current: list[float] = Field(min_length=2)
    bins: int = Field(default=10, ge=2, le=50)
