"""Validated domain models; UTC timestamps and immutable measurement identity."""
from dataclasses import dataclass
from datetime import datetime
from math import isfinite

@dataclass(frozen=True)
class QualitySpec:
    metric: str
    lsl: float
    usl: float
    target: float
    unit: str = ""
    def __post_init__(self):
        if not self.metric or not (isfinite(self.lsl) and isfinite(self.usl) and isfinite(self.target)):
            raise ValueError("invalid specification")
        if not self.lsl < self.usl or not self.lsl <= self.target <= self.usl:
            raise ValueError("require LSL < USL and target within limits")

@dataclass(frozen=True)
class Reading:
    event_id: str
    timestamp: str
    line: str
    machine: str
    metric: str
    lot: str
    value: float
    def __post_init__(self):
        if not all((self.event_id, self.line, self.machine, self.metric, self.lot)):
            raise ValueError("required reading identity fields")
        if not isfinite(self.value):
            raise ValueError("non-finite measurement")
        try:
            dt = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValueError("invalid ISO timestamp") from e
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("timestamp must include timezone")

@dataclass(frozen=True)
class Baseline:
    center: float
    sigma: float
    n: int
    method: str
    def __post_init__(self):
        if self.n < 2 or self.sigma <= 0 or not all(map(isfinite, (self.center, self.sigma))):
            raise ValueError("invalid baseline")
