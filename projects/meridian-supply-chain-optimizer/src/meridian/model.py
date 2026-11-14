from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class Route:
    source: str
    destination: str
    capacity: int
    unit_cost: int

@dataclass(frozen=True)
class Scenario:
    supply: Mapping[str, int]
    demand: Mapping[str, int]
    routes: tuple[Route, ...]

    def validate(self) -> None:
        if any(v < 0 for v in (*self.supply.values(), *self.demand.values())):
            raise ValueError("Negative supply or demand")
        if any(r.capacity < 0 or r.unit_cost < 0 for r in self.routes):
            raise ValueError("Negative route capacity or cost")
        if len({(r.source, r.destination) for r in self.routes}) != len(self.routes):
            raise ValueError("Duplicate routes")
        if any(r.source not in self.supply or r.destination not in self.demand for r in self.routes):
            raise ValueError("Unknown route endpoint")
