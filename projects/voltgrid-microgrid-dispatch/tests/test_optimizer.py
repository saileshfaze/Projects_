import math
import pytest
from voltgrid.analytics import validate_solution
from voltgrid.domain import Scenario
from voltgrid.optimizer import OptimizationError, solve

def test_dispatch_improves_tou_cost(scenario):
    result = solve(scenario)
    assert result["status"] == "optimal"
    assert result["totals"]["total_cost_usd"] < result["baseline"]["total_cost_usd"]
    assert result["savings_vs_no_storage_usd"] > 0
    assert validate_solution(scenario, result) == []
    assert math.isclose(result["objective_usd"], result["totals"]["total_cost_usd"],
                        abs_tol=0.0001)

def test_solar_curtailment_when_export_and_battery_disabled(scenario):
    payload = scenario.model_dump(mode="json")
    for slot in payload["slots"]:
        slot["load_kw"] = 0
        slot["solar_kw"] = 10
    payload["grid"]["max_export_kw"] = 0
    payload["battery"]["max_charge_kw"] = 0
    payload["battery"]["max_discharge_kw"] = 0
    result = solve(Scenario.model_validate(payload))
    assert math.isclose(result["totals"]["curtailed_kwh"], 40, abs_tol=0.001)

def test_infeasible_grid_cap_fails_explicitly(scenario):
    payload = scenario.model_dump(mode="json")
    payload["grid"]["max_import_kw"] = 1
    payload["battery"]["max_discharge_kw"] = 0
    with pytest.raises(OptimizationError):
        solve(Scenario.model_validate(payload))

@pytest.mark.parametrize("price", [0.12, 0.25, 0.40])
def test_energy_invariants_at_different_tariffs(scenario, price):
    payload = scenario.model_dump(mode="json")
    for slot in payload["slots"]:
        slot["import_price_usd_per_kwh"] = price
    updated = Scenario.model_validate(payload)
    assert not validate_solution(updated, solve(updated))
