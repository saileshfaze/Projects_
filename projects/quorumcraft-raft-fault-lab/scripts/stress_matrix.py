"""Run bounded deterministic fault-injection experiments across seeds."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from quorumcraft import Cluster, check_safety
from quorumcraft.metrics import evaluate


def experiment(seed: int) -> dict:
    cluster = Cluster(seed=seed, loss=0.06)
    for tick in range(250):
        if tick % 17 == 0:
            cluster.submit({"op": "increment", "key": "count", "value": 1}, f"{seed}-{tick}")
        if tick == 70:
            cluster.partition(["n1", "n2"], ["n3", "n4", "n5"])
        if tick == 130:
            cluster.heal()
        if tick == 170:
            cluster.crash("n4")
        if tick == 195:
            cluster.recover("n4")
        cluster.tick()
    check_safety(cluster.nodes)
    metrics = evaluate(cluster)
    return {"seed": seed, "ticks": metrics["ticks"],
            "leader_available_fraction": metrics["leader_available_fraction"],
            "leadership_transitions": metrics["leadership_transitions"],
            "max_committed_index": metrics["max_committed_index"],
            "messages_dropped": metrics["network"]["dropped"],
            "audit_valid": metrics["audit_valid"]}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    if not 1 <= args.seeds <= 1000:
        parser.error("seeds must be between 1 and 1000")
    rows = [experiment(seed) for seed in range(args.seeds)]
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    assert all(row["audit_valid"] for row in rows)
    print(f"{len(rows)} seeded simulations completed; all safety checks passed")


if __name__ == "__main__":
    main()
