"""Seeded, reproducible mutations for parser robustness exercises."""
import random
from dataclasses import dataclass
@dataclass(frozen=True)
class Mutation:
    operation: str
    offset: int
    data: bytes

def mutate(data: bytes, rng: random.Random) -> Mutation:
    operation=rng.choice(("flip","truncate","insert","duplicate","zero"))
    if operation=="flip" and data:
        i=rng.randrange(len(data)); b=bytearray(data); b[i]^=1<<rng.randrange(8)
        return Mutation(operation,i,bytes(b))
    if operation=="truncate" and data:
        i=rng.randrange(len(data)); return Mutation(operation,i,data[:i])
    if operation=="insert":
        i=rng.randrange(len(data)+1); return Mutation(operation,i,data[:i]+bytes([rng.randrange(256)])+data[i:])
    if operation=="duplicate" and data:
        i=rng.randrange(len(data)); return Mutation(operation,i,data[:i]+data[i:i+1]+data[i:])
    if data:
        i=rng.randrange(len(data)); return Mutation("zero",i,data[:i]+b"\x00"+data[i+1:])
    return Mutation("insert",0,b"\x00")
