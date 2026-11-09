"""Deterministic synthetic demand perturbations and resilience experiments."""
import random
from statistics import mean
from .model import Network,Pipe
from .solver import solve

def scaled(network,factors):
    if any(x not in network.demands or f<0 for x,f in factors.items()):raise ValueError('invalid factors')
    return Network(network.reservoir,network.reservoir_head,
                   {k:v*factors.get(k,1) for k,v in network.demands.items()},network.pipes)

def pipe_outage(network,pipe_name):
    if pipe_name not in {p.name for p in network.pipes}:raise ValueError('unknown pipe')
    return Network(network.reservoir,network.reservoir_head,network.demands,
                   tuple(p for p in network.pipes if p.name!=pipe_name))

def simulate(network,seed=42,trials=100,variation=0.15,min_head=20):
    if trials<1 or variation<0:raise ValueError('invalid experiment')
    rng=random.Random(seed);results=[]
    for i in range(trials):
        factors={k:max(0,1+rng.gauss(0,variation)) for k in network.demands}
        result=solve(scaled(network,factors))
        results.append({'trial':i,'converged':result.converged,
                        'min_head':min(result.heads[k] for k in network.demands),
                        'below_threshold':any(result.heads[k]<min_head for k in network.demands)})
    return {'seed':seed,'trials':trials,'converged':sum(x['converged'] for x in results),
            'threshold_failures':sum(x['below_threshold'] for x in results),
            'mean_min_head':mean(x['min_head'] for x in results), 'samples':results}
