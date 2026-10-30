"""Validated domain types and JSON interchange helpers."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from math import isfinite

@dataclass(frozen=True)
class Fix:
    t: float
    lat: float
    lon: float
    alt_ft: float

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.t, self.lat, self.lon, self.alt_ft)):
            raise ValueError("non-finite flight fix")
        if not -90 <= self.lat <= 90 or not -180 <= self.lon <= 180:
            raise ValueError("invalid coordinates")
        if self.alt_ft < -1500 or self.alt_ft > 100000:
            raise ValueError("altitude outside supported range")

@dataclass(frozen=True)
class Flight:
    callsign: str
    fixes: tuple[Fix, ...]

    def __post_init__(self):
        if not self.callsign or len(self.callsign) > 24 or not all(c.isalnum() or c in '-_' for c in self.callsign):
            raise ValueError("invalid callsign")
        if len(self.fixes) < 2:
            raise ValueError("at least two fixes required")
        if any(b.t <= a.t for a,b in zip(self.fixes, self.fixes[1:])):
            raise ValueError("fix timestamps must be strictly increasing")

@dataclass(frozen=True)
class Thresholds:
    horizontal_nm: float = 5.0
    vertical_ft: float = 1000.0

    def __post_init__(self):
        if not all(isfinite(v) and v > 0 for v in (self.horizontal_nm,self.vertical_ft)):
            raise ValueError("thresholds must be finite and positive")

@dataclass(frozen=True)
class Conflict:
    a: str
    b: str
    entry_s: float
    exit_s: float
    closest_s: float
    min_horizontal_nm: float
    vertical_at_closest_ft: float

    def to_dict(self):
        return asdict(self)

def parse_flights(payload: dict) -> tuple[Flight, ...]:
    if not isinstance(payload, dict) or not isinstance(payload.get('flights'),list):
        raise ValueError("expected object with flights list")
    flights=[]
    if len(payload['flights']) > 200:
        raise ValueError("maximum 200 flights")
    for row in payload['flights']:
        fixes=tuple(Fix(**fix) for fix in row['fixes'])
        if len(fixes)>500:
            raise ValueError("maximum 500 fixes per flight")
        flights.append(Flight(row['callsign'],fixes))
    if len(set(f.callsign for f in flights)) != len(flights):
        raise ValueError("duplicate callsign")
    return tuple(flights)

def flights_payload(flights: tuple[Flight,...]) -> dict:
    return {'flights':[asdict(f) for f in flights]}
