"""Benchmark without fabricated performance claims."""
import json
import statistics
import time
from pathlib import Path
from voltgrid.domain import Scenario
from voltgrid.optimizer import solve

scenario = Scenario.model_validate_json(
    (Path(__file__).resolve().parents[1] / "data/demo_scenario.json").read_text()
)
samples = []
for _ in range(5):
    started = time.perf_counter()
    result = solve(scenario)
    samples.append(time.perf_counter() - started)
assert result["status"] == "optimal"
print(json.dumps({"runs": len(samples), "mean_seconds": statistics.mean(samples),
                  "median_seconds": statistics.median(samples),
                  "intervals": len(scenario.slots)}, indent=2))
