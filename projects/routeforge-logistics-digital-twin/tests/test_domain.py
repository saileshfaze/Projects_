import pytest
from routeforge.domain import parse_problem

def test_valid_problem(problem):
    assert len(problem.jobs) == 7
    assert len(problem.vehicles) == 3

def test_duplicate_jobs(raw_problem):
    raw_problem["jobs"].append(dict(raw_problem["jobs"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        parse_problem(raw_problem)

def test_bad_coordinate(raw_problem):
    raw_problem["depot"]["lat"] = 120
    with pytest.raises(ValueError, match="latitude"):
        parse_problem(raw_problem)

def test_invalid_window(raw_problem):
    raw_problem["jobs"][0]["earliest"] = 800
    raw_problem["jobs"][0]["latest"] = 500
    with pytest.raises(ValueError, match="Invalid job"):
        parse_problem(raw_problem)

def test_empty_fleet(raw_problem):
    raw_problem["vehicles"] = []
    with pytest.raises(ValueError, match="At least one"):
        parse_problem(raw_problem)
