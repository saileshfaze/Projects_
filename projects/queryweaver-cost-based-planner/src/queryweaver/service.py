"""Stateless planning service with explicit resource limits."""
from __future__ import annotations
from functools import lru_cache
from .catalog import from_rows
from .engine import execute, canonical
from .parser import parse
from .planner import naive_plan, optimize, explain, to_dot
from .synthetic import generate

DEFAULT_SQL = ("SELECT c.id, o.id, p.price FROM orders o "
               "JOIN customers c ON o.customer_id = c.id "
               "JOIN products p ON o.product_id = p.id "
               "WHERE c.age >= 30 AND p.price > 50 LIMIT 25")


@lru_cache(maxsize=16)
def fixture(seed: int = 2026):
    return generate(seed=seed)


def analyze(sql: str = DEFAULT_SQL, seed: int = 2026, run: bool = False,
            allow_cross: bool = False) -> dict:
    tables = fixture(seed)
    query = parse(sql)
    catalog = from_rows(tables, {"orders": {"id", "customer_id", "product_id"},
                                 "customers": {"id"}, "products": {"id"}, "regions": {"id"}})
    plan = optimize(query, catalog, allow_cross=allow_cross)
    baseline = naive_plan(query, catalog)
    result = {"plan": plan.to_dict(), "explain": explain(plan), "dot": to_dot(plan),
              "baseline_cost": round(baseline.cost, 4),
              "optimized_cost": round(plan.cost, 4),
              "estimated_improvement": round(baseline.cost / max(plan.cost, 1e-9), 4)}
    if run:
        rows, stats = execute(plan, query, tables)
        result.update({"rows": rows, "actual_rows": len(rows), "execution": stats.to_dict()})
        # Query results are sets/multisets without ORDER BY. LIMIT changes semantics across plans.
        if query.limit is None:
            original, _ = execute(baseline, query, tables)
            result["equivalent_to_baseline"] = canonical(rows) == canonical(original)
    return result
