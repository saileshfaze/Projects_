"""CLI for a deterministic logistics optimization experiment."""
import argparse
import json
from .ingest import load_problem, dump_json
from .optimizer import optimize
from .scenario import simulate
from .baseline import compare

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem")
    parser.add_argument("--output", default="artifacts/plan.json")
    args = parser.parse_args()
    problem = load_problem(args.problem)
    plan = optimize(problem)
    plan["baseline"] = compare(problem, plan)
    plan["stress_test"] = simulate(problem, plan)
    dump_json(plan, args.output)
    print(json.dumps({"plan_id": plan["plan_id"], "output": args.output}))

if __name__ == "__main__":
    main()
