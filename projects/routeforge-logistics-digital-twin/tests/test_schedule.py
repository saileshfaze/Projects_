from routeforge.schedule import evaluate_route

def test_empty_route(problem):
    assert evaluate_route(problem, problem.vehicles[0], [])["cost"] == 0

def test_single_stop(problem):
    route = evaluate_route(problem, problem.vehicles[0], ["CE-001"])
    assert route is not None
    assert route["stops"][0]["service_start_min"] >= 500

def test_capacity_violation(problem):
    assert evaluate_route(problem, problem.vehicles[0], ["CE-002", "CE-004", "CE-006"]) is None

def test_duplicate_job_rejected(problem):
    import pytest
    with pytest.raises(ValueError):
        evaluate_route(problem, problem.vehicles[0], ["CE-001", "CE-001"])
