"""Validated network models and Darcy-style quadratic head loss."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Pipe:
    name: str
    start: str
    end: str
    resistance: float
    def __post_init__(self):
        if not self.name or self.start == self.end or not isfinite(self.resistance) or self.resistance <= 0:
            raise ValueError("invalid pipe")

@dataclass(frozen=True)
class Network:
    reservoir: str
    reservoir_head: float
    demands: dict[str, float]
    pipes: tuple[Pipe, ...]
    def __post_init__(self):
        if not isfinite(self.reservoir_head) or not self.pipes or self.reservoir in self.demands:
            raise ValueError("invalid network")
        if any(not isfinite(v) or v < 0 for v in self.demands.values()):
            raise ValueError("invalid demand")
        nodes = {self.reservoir, *self.demands}
        if any(p.start not in nodes or p.end not in nodes for p in self.pipes):
            raise ValueError("unknown pipe endpoint")
        if len({p.name for p in self.pipes}) != len(self.pipes):
            raise ValueError("duplicate pipe")
        reached = {self.reservoir}
        while True:
            more = reached | {p.end for p in self.pipes if p.start in reached} | {p.start for p in self.pipes if p.end in reached}
            if more == reached: break
            reached = more
        if reached != nodes: raise ValueError("disconnected network")

def from_dict(data):
    return Network(data['reservoir'], float(data['reservoir_head']),
                   {str(k):float(v) for k,v in data['demands'].items()},
                   tuple(Pipe(str(p['name']),str(p['start']),str(p['end']),float(p['resistance'])) for p in data['pipes']))

def to_dict(n):
    return {'reservoir':n.reservoir,'reservoir_head':n.reservoir_head,'demands':n.demands,
            'pipes':[vars(p) for p in n.pipes]}
