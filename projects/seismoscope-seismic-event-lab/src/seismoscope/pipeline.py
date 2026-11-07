"""Event processing orchestrator."""
from dataclasses import asdict
from .synthetic import network,generate
from .signal import detect
from .associate import associate
from .locate import locate

def run(seed=42):
    stations=network()
    traces=generate(seed=seed)
    picks=[pick for code,trace in traces.items() for pick in detect(trace,code,stations[code].sample_hz)]
    groups=associate(picks)
    events=[locate(group,stations) for group in groups]
    return {'seed':seed,'stations':len(stations),'samples_per_station':len(next(iter(traces.values()))),'picks':[asdict(p) for p in picks],'events':[asdict(e) for e in events]}
