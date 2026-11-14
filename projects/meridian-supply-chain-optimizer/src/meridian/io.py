import json
from pathlib import Path
from .model import Scenario,Route

def load(path):
    obj=json.loads(Path(path).read_text())
    return Scenario(obj['supply'],obj['demand'],tuple(Route(**item) for item in obj['routes']))

def report(result):
    return {'shipments':result.shipments,'fulfilled':result.fulfilled,'requested':result.requested,'total_cost':result.total_cost,'unmet':result.unmet}
