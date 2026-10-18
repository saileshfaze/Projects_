"""Deterministic capacity- and time-window-aware insertion heuristic."""
import json
from dataclasses import asdict
from hashlib import sha256
from .domain import Problem
from .schedule import evaluate_route

def optimize(problem: Problem, *, improve: bool = True) -> dict:
    routes = {v.id: [] for v in problem.vehicles}
    unserved = []
    for job in sorted(problem.jobs, key=lambda j: (-j.priority, j.latest, j.id)):
        options = []
        for vehicle in sorted(problem.vehicles, key=lambda v: v.id):
            current = routes[vehicle.id]
            old = evaluate_route(problem, vehicle, current)
            for position in range(len(current) + 1):
                proposed = current[:position] + [job.id] + current[position:]
                result = evaluate_route(problem, vehicle, proposed)
                if result is not None:
                    options.append((round(result["cost"] - old["cost"], 6), vehicle.id, position))
        if options:
            _, vehicle_id, position = min(options)
            routes[vehicle_id].insert(position, job.id)
        else:
            unserved.append(job.id)
    if improve:
        from .improve import relocate
        relocate(problem, routes)
    active = [evaluate_route(problem, v, routes[v.id])
              for v in sorted(problem.vehicles, key=lambda v: v.id) if routes[v.id]]
    signature = json.dumps({"problem": asdict(problem), "routes": routes}, sort_keys=True)
    return {"plan_id": sha256(signature.encode()).hexdigest()[:16], "routes": active,
            "unserved_job_ids": sorted(unserved),
            "jobs_served": sum(len(r["jobs"]) for r in active), "jobs_total": len(problem.jobs),
            "total_distance_km": round(sum(r["distance_km"] for r in active), 3),
            "total_cost": round(sum(r["cost"] for r in active), 2),
            "total_emissions_kg": round(sum(r["emissions_kg"] for r in active), 3),
            "vehicles_used": len(active),
            "algorithm": "insertion+relocate" if improve else "insertion"}
