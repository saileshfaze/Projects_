"""Plan invariants, operator summaries, and cost sensitivity diagnostics."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from .model import Plan, Query


class InvalidPlan(ValueError):
    pass


@dataclass(frozen=True)
class PlanSummary:
    operators: dict[str, int]
    depth: int
    estimated_rows: float
    estimated_cost: float
    scan_aliases: tuple[str, ...]

    def to_dict(self) -> dict:
        return {"operators": self.operators, "depth": self.depth,
                "estimated_rows": round(self.estimated_rows, 4),
                "estimated_cost": round(self.estimated_cost, 4),
                "scan_aliases": list(self.scan_aliases)}


def inspect(plan: Plan, query: Query) -> PlanSummary:
    counts: Counter[str] = Counter()
    leaves: list[str] = []
    supported = {"table_scan", "index_scan", "hash_join", "nested_loop_join",
                 "index_nested_loop_join", "project", "limit"}

    def walk(node: Plan) -> int:
        if node.op not in supported:
            raise InvalidPlan(f"Unknown operator {node.op}")
        if node.rows < 0 or node.cost < 0:
            raise InvalidPlan("Negative row or cost estimate")
        counts[node.op] += 1
        if node.op in {"table_scan", "index_scan"}:
            if node.children or len(node.tables) != 1:
                raise InvalidPlan("Scan must be a leaf with one alias")
            leaves.append(node.tables[0])
            return 1
        if node.op in {"project", "limit"}:
            if len(node.children) != 1:
                raise InvalidPlan("Unary operator must have one child")
        elif len(node.children) != 2:
            raise InvalidPlan("Join must have two children")
        for child in node.children:
            if not set(child.tables).issubset(node.tables):
                raise InvalidPlan("Child references aliases absent from parent")
        if node.op.endswith("join") and set(node.children[0].tables) & set(node.children[1].tables):
            raise InvalidPlan("Join operands must not share aliases")
        return 1 + max(walk(child) for child in node.children)

    depth = walk(plan)
    expected = sorted(rel.alias for rel in query.relations)
    if sorted(leaves) != expected:
        raise InvalidPlan(f"Scan coverage mismatch: {sorted(leaves)} != {expected}")
    if sorted(plan.tables) != expected:
        raise InvalidPlan("Root aliases do not match query")
    return PlanSummary(dict(sorted(counts.items())), depth, plan.rows, plan.cost, tuple(sorted(leaves)))
