"""Write a deterministic synthetic dataset for local experiments."""

import argparse

from atlasflow.synthetic import make_rows, write_csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=320)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--out", default="data/synthetic_customers.csv")
    args = parser.parse_args()
    rows = make_rows(args.rows, args.seed)
    write_csv(args.out, rows)
    print(f"Wrote {len(rows)} synthetic records to {args.out}")
