"""Command-line scenario simulation and forecasting."""

import argparse
import json
from pathlib import Path
from uuid import uuid4

from .analytics import sustainability, validate_solution
from .domain import Scenario
from .forecast import seasonal_forecast
from .optimizer import solve
from .storage import RunStore

def main() -> None:
    parser = argparse.ArgumentParser(prog="voltgrid")
    sub = parser.add_subparsers(dest="command", required=True)
    sim = sub.add_parser("simulate", help="optimize a JSON scenario")
    sim.add_argument("scenario", type=Path)
    sim.add_argument("--db", type=Path, default=Path("data/voltgrid.sqlite3"))
    sim.add_argument("--output", type=Path)
    fc = sub.add_parser("forecast", help="forecast a JSON list of nonnegative kW readings")
    fc.add_argument("history", type=Path)
    fc.add_argument("--horizon", type=int, default=24)
    fc.add_argument("--season", type=int, default=24)
    args = parser.parse_args()
    if args.command == "forecast":
        data = json.loads(args.history.read_text(encoding="utf-8"))
        print(json.dumps(seasonal_forecast(data, args.horizon, args.season), indent=2))
        return
    scenario = Scenario.model_validate_json(args.scenario.read_text(encoding="utf-8"))
    result = solve(scenario)
    issues = validate_solution(scenario, result)
    if issues:
        raise RuntimeError(f"dispatch invariant violations: {issues}")
    result["sustainability"] = sustainability(scenario, result)
    run_id = str(uuid4())
    RunStore(args.db).save(run_id, scenario.model_dump(mode="json"), result)
    payload = json.dumps({"run_id": run_id, "result": result}, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)

if __name__ == "__main__":
    main()
