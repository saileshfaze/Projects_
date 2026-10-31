"""Repeatable correctness and latency comparison for optimizer and baseline."""
from __future__ import annotations
import statistics
import time
from .catalog import from_rows
from .diagnostics import inspect
from .engine import canonical, execute
from .parser import parse
from .planner import naive_plan, optimize
from .synthetic import generate

QUERIES = {
    "two_way": "SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id WHERE c.age>=40",
    "three_way": ("SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id "
                  "JOIN regions r ON c.region_id=r.id WHERE r.tax_rate>=0.19"),
    "four_way": ("SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id "
                 "JOIN regions r ON c.region_id=r.id "
                 "JOIN products p ON o.product_id=p.id WHERE p.price>50"),
}


def benchmark(seed: int = 2026, repetitions: int = 3, customers: int = 120,
              orders: int = 900, products: int = 40) -> list[dict]:
    if not 1 <= repetitions <= 100:
        raise ValueError("repetitions must be between 1 and 100")
    tables = generate(seed, customers, orders, products)
    catalog = from_rows(tables, {"customers": {"id"}, "orders": {"customer_id", "product_id"},
                                 "products": {"id"}, "regions": {"id"}})
    results = []
    for name, sql in QUERIES.items():
        query = parse(sql)
        fast, slow = optimize(query, catalog), naive_plan(query, catalog)
        inspect(fast, query)
        durations = {"optimized": [], "baseline": []}
        expected = None
        for label, plan in (("optimized", fast), ("baseline", slow)):
            for _ in range(repetitions):
                start = time.perf_counter()
                rows, _ = execute(plan, query, tables)
                durations[label].append((time.perf_counter() - start) * 1000)
                if expected is None:
                    expected = canonical(rows)
                elif canonical(rows) != expected:
                    raise AssertionError(f"Optimizer changed query results for {name}")
        results.append({"name": name, "seed": seed, "rows": len(expected),
                        "optimized_estimated_cost": round(fast.cost, 3),
                        "baseline_estimated_cost": round(slow.cost, 3),
                        "optimized_median_ms": round(statistics.median(durations["optimized"]), 3),
                        "baseline_median_ms": round(statistics.median(durations["baseline"]), 3),
                        "equivalent": True})
    return results
