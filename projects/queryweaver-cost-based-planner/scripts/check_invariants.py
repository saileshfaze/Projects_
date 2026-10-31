"""Seeded metamorphic tests: planner vs baseline across synthetic workloads."""
import argparse
from queryweaver.benchmark import QUERIES
from queryweaver.catalog import from_rows
from queryweaver.diagnostics import inspect
from queryweaver.engine import canonical, execute
from queryweaver.parser import parse
from queryweaver.planner import optimize, naive_plan
from queryweaver.synthetic import generate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.seeds <= 1000:
        parser.error("--seeds must be in 1..1000")
    checked = 0
    for seed in range(args.seeds):
        tables = generate(seed, customers=12, orders=50, products=8)
        catalog = from_rows(tables, {"orders": {"customer_id", "product_id"},
                                     "customers": {"id"}, "products": {"id"}, "regions": {"id"}})
        for sql in QUERIES.values():
            query = parse(sql)
            fast, slow = optimize(query, catalog), naive_plan(query, catalog)
            inspect(fast, query)
            assert canonical(execute(fast, query, tables)[0]) == canonical(execute(slow, query, tables)[0])
            checked += 1
    print(f"PASS: {checked} optimizer/baseline equivalence checks across {args.seeds} seeds")


if __name__ == "__main__":
    main()
