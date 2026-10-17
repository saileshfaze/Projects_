"""Run a physical consistency check on the synthetic demo scenario."""
from pathlib import Path
from voltgrid.analytics import validate_solution
from voltgrid.domain import Scenario
from voltgrid.optimizer import solve

ROOT = Path(__file__).resolve().parents[1]
scenario = Scenario.model_validate_json((ROOT / "data/demo_scenario.json").read_text())
result = solve(scenario)
issues = validate_solution(scenario, result)
if issues:
    raise SystemExit(f"Failed invariant checks: {issues}")
print(f"Optimal cost: ${result['totals']['total_cost_usd']:.2f} USD")
