"""Write measured benchmark results to JSON (timings are machine-dependent)."""
from pathlib import Path
import argparse
import json
from queryweaver.benchmark import benchmark


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("out/benchmark.json"))
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result = benchmark(seed=args.seed, repetitions=args.repetitions)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} benchmark cases to {args.out}")


if __name__ == "__main__":
    main()
