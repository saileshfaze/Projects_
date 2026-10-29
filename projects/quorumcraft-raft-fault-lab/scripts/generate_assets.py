"""Regenerate deterministic scenario, timeline, and metrics assets."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from quorumcraft import Cluster
from quorumcraft.metrics import evaluate
from quorumcraft.persistence import export_run
from quorumcraft.report import write_report
from quorumcraft.scenarios import demo_actions, run_scenario
from quorumcraft.synthetic import generate


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="out")
    args = parser.parse_args(argv)
    destination = Path(args.output)
    destination.mkdir(parents=True, exist_ok=True)
    generate(destination / "partition-heal.json")
    cluster = Cluster(seed=42)
    run_scenario(cluster, demo_actions(), 150)
    export_run(cluster, destination / "simulation.json")
    write_report(cluster, destination / "leadership-timeline.svg")
    (destination / "metrics.json").write_text(json.dumps(evaluate(cluster), indent=2, sort_keys=True) + "\n")
    print(f"Generated 4 reproducible artifacts in {destination}")


if __name__ == "__main__":
    main()
