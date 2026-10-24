"""Validated experiment configuration and event types."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import re

_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,95}$")


def check_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError(f"{label} must be 1-96 safe ASCII characters")
    return value


@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    salt: str
    treatment_fraction: float = 0.5
    alpha: float = 0.05
    planned_looks: int = 1
    minimum_per_arm: int = 20

    def __post_init__(self) -> None:
        check_id(self.experiment_id, "experiment_id")
        if not self.salt or len(self.salt) < 12:
            raise ValueError("salt must be at least 12 characters")
        if not 0.01 <= self.treatment_fraction <= 0.99:
            raise ValueError("treatment_fraction must be between 0.01 and 0.99")
        if not 0 < self.alpha < 0.5:
            raise ValueError("alpha must be between 0 and 0.5")
        if not 1 <= self.planned_looks <= 100:
            raise ValueError("planned_looks must be 1-100")
        if self.minimum_per_arm < 2:
            raise ValueError("minimum_per_arm must be at least 2")


@dataclass(frozen=True)
class Outcome:
    event_id: str
    experiment_id: str
    subject_id: str
    revenue: float
    preperiod_revenue: float
    converted: bool
    refunded: bool
    timestamp: str

    def __post_init__(self) -> None:
        for field in ("event_id", "experiment_id", "subject_id"):
            check_id(getattr(self, field), field)
        for field in ("revenue", "preperiod_revenue"):
            value = getattr(self, field)
            if not isinstance(value, (int, float)) or not 0 <= value < 1e9:
                raise ValueError(f"{field} must be finite and nonnegative")
        if not isinstance(self.converted, bool) or not isinstance(self.refunded, bool):
            raise ValueError("converted/refunded must be boolean")
        parsed = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must include timezone")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()
