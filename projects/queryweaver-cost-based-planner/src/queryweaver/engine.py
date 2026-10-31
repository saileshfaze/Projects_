"""Reference executor for validating optimizer equivalence, not a database engine."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .model import Column, Predicate, Query, Plan

Row = dict[str, Any]


class ExecutionError(ValueError):
    pass


def get(row: Row, value: Column | Any) -> Any:
    if isinstance(value, Column):
        key = str(value)
        if key not in row:
            raise ExecutionError(f"Column not found: {key}")
        return row[key]
    return value


def matches(row: Row, predicate: Predicate) -> bool:
    left, right = get(row, predicate.left), get(row, predicate.right)
    if left is None or right is None:
        return False
    try:
        return {"=": lambda: left == right, "!=": lambda: left != right,
                "<": lambda: left < right, "<=": lambda: left <= right,
                ">": lambda: left > right, ">=": lambda: left >= right}[predicate.op]()
    except (TypeError, KeyError) as exc:
        raise ExecutionError(f"Invalid comparison: {predicate}") from exc


@dataclass
class ExecutionStats:
    scanned: int = 0
    compared: int = 0
    produced: int = 0

    def to_dict(self) -> dict[str, int]:
        return {"scanned": self.scanned, "compared": self.compared, "produced": self.produced}


def execute(plan: Plan, query: Query, tables: dict[str, list[dict]],
            max_rows: int = 250000) -> tuple[list[Row], ExecutionStats]:
    stats = ExecutionStats()
    relations = {r.alias: r.name for r in query.relations}

    def run(node: Plan) -> list[Row]:
        if node.op in {"table_scan", "index_scan"}:
            alias = node.tables[0]
            raw = tables[relations[alias]]
            filters = [p for p in query.filters if p.left.table == alias and not isinstance(p.right, Column)]
            result = []
            for item in raw:
                stats.scanned += 1
                row = {f"{alias}.{k}": v for k, v in item.items()}
                if all(matches(row, pred) for pred in filters):
                    result.append(row)
            return result
        if node.op in {"nested_loop_join", "hash_join", "index_nested_loop_join"}:
            left, right = (run(child) for child in node.children)
            left_aliases = set(node.children[0].tables)
            right_aliases = set(node.children[1].tables)
            preds = [p for p in query.joins if
                     (p.left.table in left_aliases and p.right.table in right_aliases) or
                     (p.right.table in left_aliases and p.left.table in right_aliases)]
            output = []
            if node.op == "hash_join" and preds:
                first = preds[0]
                lcol = first.left if first.left.table in left_aliases else first.right
                rcol = first.right if first.right.table in right_aliases else first.left
                buckets: dict[Any, list[Row]] = {}
                for row in right:
                    key = get(row, rcol)
                    if key is not None:
                        buckets.setdefault(key, []).append(row)
                for lrow in left:
                    key = get(lrow, lcol)
                    for rrow in buckets.get(key, []) if key is not None else []:
                        stats.compared += 1
                        merged = {**lrow, **rrow}
                        if all(matches(merged, pred) for pred in preds):
                            output.append(merged)
            else:
                for lrow in left:
                    for rrow in right:
                        stats.compared += 1
                        merged = {**lrow, **rrow}
                        if all(matches(merged, pred) for pred in preds):
                            output.append(merged)
            if len(output) > max_rows:
                raise ExecutionError("Intermediate result exceeds max_rows")
            return output
        if node.op == "project":
            columns = [str(c) for c in query.columns or ()]
            return [{key: row[key] for key in columns} for row in run(node.children[0])]
        if node.op == "limit":
            return run(node.children[0])[:node.detail["count"]]
        raise ExecutionError(f"Unknown operator {node.op}")

    output = run(plan)
    # Filters spanning two relations are evaluated after joins (WHERE clause).
    cross_filters = [p for p in query.filters if isinstance(p.right, Column)]
    if cross_filters:
        # Query projections must not discard columns needed for the predicate.
        # Evaluate before project/limit by refusing unsupported cases instead of silently mis-evaluating.
        raise ExecutionError("Column-to-column WHERE predicates are not supported")
    stats.produced = len(output)
    return output, stats


def canonical(rows: list[Row]) -> list[str]:
    import json
    return sorted(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows)
