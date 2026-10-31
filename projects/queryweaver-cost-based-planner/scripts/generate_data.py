"""Rebuild all deterministic demonstration CSV fixtures."""
from pathlib import Path
import argparse
import json
from queryweaver.synthetic import generate, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data"))
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    print(json.dumps(save(generate(seed=args.seed, customers=24, orders=160, products=12), args.out)))


if __name__ == "__main__":
    main()
