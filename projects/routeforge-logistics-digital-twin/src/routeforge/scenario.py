"""Reproducible Monte Carlo stress tests of a fixed dispatch plan."""
from dataclasses import replace
from random import Random
from .domain import Problem
from .schedule import evaluate_route

def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    rank = (len(values) - 1) * fraction
    low = int(rank)
    high = min(low + 1, len(values) - 1)
    return round(values[low] * (high - rank) + values[high] * (rank - low), 2)

def simulate(problem: Problem, plan: dict, *, trials: int = 200, seed: int = 42,
             speed_jitter: float = 0.20, demand_jitter: float = 0.10) -> dict:
    if not 1 <= trials <= 10000:
        raise ValueError("trials must be between 1 and 10000")
    if not (0 <= speed_jitter < 1 and 0 <= demand_jitter < 1):
        raise ValueError("jitter must be in [0,1)")
    rng = Random(seed)
    costs = []
    routes = [(r["vehicle_id"], r["jobs"]) for r in plan["routes"]]
    if any(vid not in {v.id for v in problem.vehicles} for vid, _ in routes):
        raise ValueError("Unknown vehicle in plan")
    for _ in range(trials):
        perturbed = replace(problem,
            jobs=tuple(replace(j, demand=j.demand * rng.uniform(1-demand_jitter, 1+demand_jitter))
                       for j in problem.jobs),
            vehicles=tuple(replace(v, speed_kmh=v.speed_kmh * rng.uniform(1-speed_jitter, 1+speed_jitter))
                           for v in problem.vehicles))
        trial = [evaluate_route(perturbed, next(v for v in perturbed.vehicles if v.id == vid), jobs)
                 for vid, jobs in routes]
        if all(r is not None for r in trial):
            costs.append(sum(r["cost"] for r in trial))
    return {"trials": trials, "seed": seed, "feasibility_rate": round(len(costs)/trials, 4),
            "cost_p50_feasible": percentile(costs, .5),
            "cost_p95_feasible": percentile(costs, .95),
            "cost_samples_feasible": len(costs),
            "note": "Cost percentiles condition on feasible trials; failures counted separately."}
