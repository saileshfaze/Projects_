"""CLI for reproducible demonstrations; seeded RNG is NOT secure for real DP releases."""
import argparse
import csv
import json
import random
from pathlib import Path
from .core import PrivacyLedger, bound_contributions, private_histogram, private_mean

def main():
    parser = argparse.ArgumentParser(description="PrivacyLens synthetic DP analytics")
    parser.add_argument("csv", type=Path)
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--budget", type=float, default=2.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    with args.csv.open(newline="", encoding="utf-8") as f:
        rows = bound_contributions(csv.DictReader(f), "user_id")
    ledger = PrivacyLedger(args.budget)
    rng = random.Random(args.seed)
    hist = private_histogram(rows, "region", ["north", "south", "west"], args.epsilon, ledger, rng)
    result = {"noisy_region_counts": hist, "privacy_ledger": ledger.report(),
              "warning": "Deterministic RNG for demonstration only; NOT secure for real releases"}
    print(json.dumps(result, indent=2))
if __name__ == "__main__":
    main()
