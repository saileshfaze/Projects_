"""Transparent first-fit baseline for measuring optimization gains."""
from .domain import Problem
from .schedule import evaluate_route

def first_fit(problem: Problem) -> dict:
    routes = {v.id: [] for v in problem.vehicles}
    unserved = []
    for job in problem.jobs:
        for vehicle in problem.vehicles:
            proposed = routes[vehicle.id] + [job.id]
            if evaluate_route(problem, vehicle, proposed) is not None:
                routes[vehicle.id] = proposed
                break
        else:
            unserved.append(job.id)
    active = [evaluate_route(problem, v, routes[v.id]) for v in problem.vehicles if routes[v.id]]
    return {"total_cost": round(sum(r["cost"] for r in active), 2),
            "jobs_served": sum(len(r["jobs"]) for r in active),
            "unserved_job_ids": unserved, "routes": active}

def compare(problem: Problem, plan: dict) -> dict:
    baseline = first_fit(problem)
    return {"baseline_cost": baseline["total_cost"], "optimized_cost": plan["total_cost"],
            "baseline_served": baseline["jobs_served"], "optimized_served": plan["jobs_served"],
            "cost_delta_eur": round(baseline["total_cost"] - plan["total_cost"], 2),
            "warning": "Costs are comparable only when served-job counts match."}
