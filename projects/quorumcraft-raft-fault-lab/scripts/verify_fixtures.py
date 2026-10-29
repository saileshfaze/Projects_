"""Validate synthetic sample assets against deterministic regeneration."""
from __future__ import annotations
import json
from pathlib import Path
from quorumcraft import Cluster
from quorumcraft.metrics import evaluate
from quorumcraft.scenarios import actions_from_dict, run_scenario


def main():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "data/partition-heal.json").read_text())
    metrics = json.loads((root / "data/demo-metrics.json").read_text())
    cluster = Cluster(size=data["nodes"], seed=data["seed"])
    run_scenario(cluster, actions_from_dict(data["actions"]), data["until"])
    actual = evaluate(cluster)
    assert metrics == actual, "metrics fixture differs from reproducible simulation"
    assert all(node.state.get("orders") == 15 for node in cluster.nodes.values())
    print("Synthetic scenario and metrics fixture verified")


if __name__ == "__main__":
    main()
