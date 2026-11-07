"""Validated, immutable geophysical domain records."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Station:
    code: str
    x_km: float
    y_km: float
    sample_hz: float = 50.0
    def __post_init__(self):
        if not self.code or self.sample_hz <= 0 or not all(map(isfinite,(self.x_km,self.y_km,self.sample_hz))):
            raise ValueError("invalid station")

@dataclass(frozen=True)
class Pick:
    station: str
    time_s: float
    score: float
    def __post_init__(self):
        if not self.station or not isfinite(self.time_s) or not isfinite(self.score) or self.score < 0:
            raise ValueError("invalid pick")

@dataclass(frozen=True)
class Event:
    origin_s: float
    x_km: float
    y_km: float
    residual_s: float
    stations: tuple[str, ...]
