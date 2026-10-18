"""Validated immutable entities for a single-depot delivery planning problem."""
from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping

@dataclass(frozen=True)
class Depot:
    id: str
    lat: float
    lon: float

@dataclass(frozen=True)
class Job:
    id: str
    lat: float
    lon: float
    demand: float
    earliest: int
    latest: int
    service_min: int = 5
    priority: int = 1

@dataclass(frozen=True)
class Vehicle:
    id: str
    capacity: float
    shift_start: int
    shift_end: int
    speed_kmh: float = 35.0
    fixed_cost: float = 12.0
    cost_per_km: float = 0.9
    emissions_g_per_km: float = 260.0
    max_km: float = 300.0

@dataclass(frozen=True)
class Problem:
    depot: Depot
    jobs: tuple[Job, ...]
    vehicles: tuple[Vehicle, ...]

def _coordinate(lat: float, lon: float) -> None:
    if not (isfinite(lat) and isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

def parse_problem(raw: Mapping[str, Any]) -> Problem:
    """Reject ambiguous identifiers, invalid units and impossible time windows."""
    try:
        depot = Depot(**raw["depot"])
        jobs = tuple(Job(**item) for item in raw["jobs"])
        vehicles = tuple(Vehicle(**item) for item in raw["vehicles"])
    except (KeyError, TypeError) as exc:
        raise ValueError("Missing or malformed problem fields") from exc
    _coordinate(depot.lat, depot.lon)
    if not jobs or not vehicles:
        raise ValueError("At least one job and vehicle required")
    for values, kind in ((jobs, "job"), (vehicles, "vehicle")):
        ids = [x.id for x in values]
        if any(not isinstance(x, str) or not x.strip() for x in ids) or len(ids) != len(set(ids)):
            raise ValueError("Duplicate or empty " + kind + " IDs")
    for job in jobs:
        _coordinate(job.lat, job.lon)
        if not (isfinite(job.demand) and job.demand > 0 and 0 <= job.earliest <= job.latest <= 1440
                and job.service_min >= 0 and job.priority >= 1):
            raise ValueError("Invalid job: " + job.id)
    for vehicle in vehicles:
        if not (isfinite(vehicle.capacity) and vehicle.capacity > 0
                and 0 <= vehicle.shift_start < vehicle.shift_end <= 1440
                and all(isfinite(x) and x > 0 for x in
                        (vehicle.speed_kmh, vehicle.cost_per_km, vehicle.max_km))
                and isfinite(vehicle.fixed_cost) and vehicle.fixed_cost >= 0
                and isfinite(vehicle.emissions_g_per_km) and vehicle.emissions_g_per_km >= 0):
            raise ValueError("Invalid vehicle: " + vehicle.id)
    return Problem(depot, jobs, vehicles)
