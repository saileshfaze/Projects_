"""Selinger-style left-deep dynamic programming optimizer with access path choices."""
from __future__ import annotations
import itertools
import math
from .catalog import Catalog
from .model import Column, Plan, Predicate, Query


class PlanningError(ValueError):
    pass


def predicates_for(query: Query, alias: str) -> tuple[Predicate, ...]:
    return tuple(p for p in query.filters if p.left.table == alias and not isinstance(p.right, Column))


def scans(query: Query, catalog: Catalog) -> dict[str, Plan]:
    result = {}
    for rel in query.relations:
        base = catalog.tables[rel.name]
        filters = predicates_for(query, rel.alias)
        selectivity = math.prod(catalog.selectivity(p, query) for p in filters)
        rows = max(0.0, base.rows * selectivity)
        cost = float(base.rows) + 0.1 * rows
        best = Plan("table_scan", (rel.alias,), rows, cost, {"table": rel.name})
        for p in filters:
            if catalog.column(p.left, query).indexed and p.op == "=":
                index_cost = math.log2(base.rows + 1) + 1.5 * rows
                if index_cost < best.cost:
                    best = Plan("index_scan", (rel.alias,), rows, index_cost,
                                {"table": rel.name, "column": p.left.name})
        if filters:
            best.detail["filters"] = [str(p.left) + p.op + str(p.right) for p in filters]
        result[rel.alias] = best
    return result


def connecting(query: Query, existing: frozenset[str], incoming: str) -> list[Predicate]:
    return [p for p in query.joins if
            (p.left.table in existing and p.right.table == incoming) or
            (p.right.table in existing and p.left.table == incoming)]


def optimize(query: Query, catalog: Catalog, *, allow_cross: bool = False,
             allow_hash: bool = True) -> Plan:
    catalog.validate(query)
    access = scans(query, catalog)
    dp: dict[frozenset[str], Plan] = {frozenset([a]): p for a, p in access.items()}
    aliases = tuple(access)
    for size in range(2, len(aliases) + 1):
        for subset_tuple in itertools.combinations(aliases, size):
            subset = frozenset(subset_tuple)
            choices = []
            for incoming in subset:
                prior = subset - {incoming}
                left = dp.get(prior)
                if left is None:
                    continue
                right = access[incoming]
                predicates = connecting(query, prior, incoming)
                if not predicates and not allow_cross:
                    continue
                selectivity = math.prod(catalog.selectivity(p, query) for p in predicates) if predicates else 1.0
                rows = max(0.0, left.rows * right.rows * selectivity)
                details = {"on": [f"{p.left}={p.right}" for p in predicates], "cross": not bool(predicates)}
                nested_cost = left.cost + right.cost + left.rows * max(1.0, right.rows)
                choices.append(Plan("nested_loop_join", tuple(sorted(subset)), rows, nested_cost,
                                    details, (left, right)))
                if predicates and allow_hash:
                    hash_cost = left.cost + right.cost + 1.2 * (left.rows + right.rows) + 0.1 * rows
                    choices.append(Plan("hash_join", tuple(sorted(subset)), rows, hash_cost,
                                        details, (left, right)))
                if predicates:
                    # Index nested-loop is applicable when the incoming relation's join key is indexed.
                    for pred in predicates:
                        incoming_col = pred.left if pred.left.table == incoming else pred.right
                        if catalog.column(incoming_col, query).indexed:
                            lookup = math.log2(catalog.tables[next(r.name for r in query.relations if r.alias == incoming)].rows + 1)
                            idx_cost = left.cost + left.rows * (lookup + max(1, right.rows * selectivity))
                            choices.append(Plan("index_nested_loop_join", tuple(sorted(subset)), rows,
                                                idx_cost, details, (left, right)))
            if choices:
                dp[subset] = min(choices, key=lambda p: (p.cost, p.op, p.tables))
    full = frozenset(aliases)
    if full not in dp:
        raise PlanningError("Disconnected join graph; enable allow_cross to plan a cross join")
    plan = dp[full]
    if query.columns is not None:
        plan = Plan("project", plan.tables, plan.rows, plan.cost + plan.rows * 0.02,
                    {"columns": [str(c) for c in query.columns]}, (plan,))
    if query.limit is not None:
        plan = Plan("limit", plan.tables, min(plan.rows, query.limit), plan.cost + 0.01,
                    {"count": query.limit}, (plan,))
    return plan


def naive_plan(query: Query, catalog: Catalog) -> Plan:
    """A fixed input-order nested-loop baseline for cost comparison."""
    catalog.validate(query)
    access = scans(query, catalog)
    plan = access[query.relations[0].alias]
    for rel in query.relations[1:]:
        right = access[rel.alias]
        preds = connecting(query, frozenset(plan.tables), rel.alias)
        selectivity = math.prod(catalog.selectivity(p, query) for p in preds) if preds else 1.0
        plan = Plan("nested_loop_join", tuple(sorted((*plan.tables, rel.alias))),
                    plan.rows * right.rows * selectivity,
                    plan.cost + right.cost + plan.rows * max(1, right.rows),
                    {"on": [f"{p.left}={p.right}" for p in preds], "cross": not bool(preds)},
                    (plan, right))
    if query.columns is not None:
        plan = Plan("project", plan.tables, plan.rows, plan.cost + plan.rows * 0.02,
                    {"columns": [str(c) for c in query.columns]}, (plan,))
    if query.limit is not None:
        plan = Plan("limit", plan.tables, min(plan.rows, query.limit), plan.cost + 0.01,
                    {"count": query.limit}, (plan,))
    return plan


def explain(plan: Plan, indent: int = 0) -> str:
    head = "  " * indent + f"{plan.op} rows={plan.rows:.2f} cost={plan.cost:.2f}"
    return "\n".join([head] + [explain(child, indent + 1) for child in plan.children])


def to_dot(plan: Plan) -> str:
    lines = ["digraph query_plan {", "  rankdir=BT;", '  node [shape=box,style="rounded,filled",fillcolor="#e8f0fe",fontname="Helvetica"];']
    counter = 0

    def walk(node: Plan) -> int:
        nonlocal counter
        me = counter
        counter += 1
        lines.append(f'  n{me} [label="{node.op}\\nrows={node.rows:.1f}\\ncost={node.cost:.1f}"];')
        for child in node.children:
            child_id = walk(child)
            lines.append(f"  n{child_id} -> n{me};")
        return me
    walk(plan)
    return "\n".join(lines + ["}"])
