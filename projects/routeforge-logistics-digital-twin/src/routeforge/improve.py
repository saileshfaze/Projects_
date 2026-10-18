"""Bounded best-improvement inter-vehicle relocation search."""
from .domain import Problem
from .schedule import evaluate_route

def relocate(problem: Problem, routes: dict[str, list[str]], passes: int = 5) -> None:
    vehicles = {v.id: v for v in problem.vehicles}
    for _ in range(passes):
        best = None
        for source in sorted(routes):
            original = evaluate_route(problem, vehicles[source], routes[source])
            for job in list(routes[source]):
                shortened = [j for j in routes[source] if j != job]
                reduced = evaluate_route(problem, vehicles[source], shortened)
                for target in sorted(routes):
                    if target == source:
                        continue
                    before = evaluate_route(problem, vehicles[target], routes[target])
                    for position in range(len(routes[target]) + 1):
                        extended = routes[target][:position] + [job] + routes[target][position:]
                        after = evaluate_route(problem, vehicles[target], extended)
                        if after is None:
                            continue
                        delta = reduced["cost"] + after["cost"] - original["cost"] - before["cost"]
                        candidate = (round(delta, 6), source, job, target, position)
                        if delta < -0.000001 and (best is None or candidate < best):
                            best = candidate
        if best is None:
            return
        _, source, job, target, position = best
        routes[source].remove(job)
        routes[target].insert(position, job)
