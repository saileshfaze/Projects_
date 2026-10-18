from routeforge.optimizer import optimize
from routeforge.baseline import compare

def test_no_duplicate_assignments(problem):
    plan = optimize(problem)
    assigned = [j for route in plan["routes"] for j in route["jobs"]]
    assert len(assigned) == len(set(assigned))
    assert len(assigned) + len(plan["unserved_job_ids"]) == len(problem.jobs)

def test_determinism(problem):
    assert optimize(problem) == optimize(problem)

def test_all_routes_feasible(problem):
    from routeforge.schedule import evaluate_route
    fleet = {v.id: v for v in problem.vehicles}
    for route in optimize(problem)["routes"]:
        assert evaluate_route(problem, fleet[route["vehicle_id"]], route["jobs"]) is not None

def test_comparison(problem):
    result = compare(problem, optimize(problem))
    assert "baseline_cost" in result
