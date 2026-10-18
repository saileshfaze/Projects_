"""Synthetic benchmark; reports wall time, coverage and cost without claiming optimality."""
import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter
from routeforge.domain import parse_problem
from routeforge.optimizer import optimize
from routeforge.baseline import compare
from generate_synthetic import generate

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output", default="artifacts/benchmark.json")
    args = parser.parse_args()
    if not 1 <= args.count <= 500 or not 1 <= args.repetitions <= 50:
        parser.error("count must be 1..500 and repetitions 1..50")
    problem = parse_problem(generate(args.count))
    timings = []
    plan = None
    for _ in range(args.repetitions):
        start = perf_counter()
        plan = optimize(problem)
        timings.append(perf_counter() - start)
    result = {"count": args.count, "repetitions": args.repetitions,
              "median_seconds": round(median(timings), 5),
              "jobs_served": plan["jobs_served"],
              "jobs_total": plan["jobs_total"],
              "baseline": compare(problem, plan)}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
