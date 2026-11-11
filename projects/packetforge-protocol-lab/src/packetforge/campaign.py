"""Deterministic mutation campaigns; no sockets or live targets."""
import random
from dataclasses import dataclass, asdict
from .wire import Frame,encode,decode
from .mutate import mutate
from .errors import FrameError
@dataclass(frozen=True)
class CampaignResult:
    seed:int
    cases:int
    accepted:int
    rejected:int
    unexpected:int
    by_operation:dict
    def to_dict(self): return asdict(self)
def run(seed=2026,cases=500):
    if cases<0 or cases>100000: raise ValueError("cases out of range")
    rng=random.Random(seed)
    accepted=rejected=unexpected=0
    operations={}
    for i in range(cases):
        original=encode(Frame(rng.randrange(4),i, rng.randbytes(rng.randrange(65))))
        change=mutate(original,rng)
        operations[change.operation]=operations.get(change.operation,0)+1
        try:
            decoded=decode(change.data)
            accepted+=1
            if encode(decoded)!=change.data: unexpected+=1
        except FrameError: rejected+=1
        except Exception: unexpected+=1
    return CampaignResult(seed,cases,accepted,rejected,unexpected,operations)
