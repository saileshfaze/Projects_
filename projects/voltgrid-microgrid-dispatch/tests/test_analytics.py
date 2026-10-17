from voltgrid.analytics import sustainability, validate_solution
from voltgrid.optimizer import solve

def test_independent_physical_checks(scenario):
    result = solve(scenario)
    assert validate_solution(scenario, result) == []
    result["schedule"][0]["grid_import_kw"] += 3
    assert any("power balance" in error for error in validate_solution(scenario, result))

def test_sustainability(scenario):
    indicators = sustainability(scenario, solve(scenario))
    assert indicators["solar_utilization_ratio"] is None
    assert "carbon_avoided_kg" in indicators
