from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class Transaction(BaseModel):
    transaction_id: str = Field(min_length=6,max_length=64)
    account_id: str = Field(min_length=3,max_length=64)
    amount_eur: float = Field(gt=0,le=100_000)
    merchant_category: str = Field(min_length=2,max_length=64)
    country: str = Field(pattern=r"^[A-Z]{2}$")
    channel: Literal["card_present","ecommerce","transfer","wallet"]
    account_age_days: int = Field(ge=0)
    tx_count_24h: int = Field(ge=0)
    avg_amount_30d: float = Field(gt=0)
    event_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("event_time")
    @classmethod
    def timezone_required(cls,value: datetime)->datetime:
        if value.tzinfo is None: raise ValueError("event_time must be timezone-aware")
        return value

class RiskDecision(BaseModel):
    transaction_id: str
    score: float = Field(ge=0,le=1)
    decision: Literal["allow","review","block"]
    reasons: list[str]
    model_version: str
