"""Cycle-safe graph analysis and reproducible dependency paths."""
from __future__ import annotations
from collections import deque
from .models import BillOfMaterials


def shortest_paths(bom: BillOfMaterials) -> dict[str, tuple[str, ...]]:
    paths = {root: (root,) for root in bom.roots}
    queue = deque(sorted(bom.roots))
    while queue:
        parent = queue.popleft()
        for child in bom.dependencies.get(parent, ()):
            if child not in paths:
                paths[child] = paths[parent] + (child,)
                queue.append(child)
    return paths


def strongly_connected_components(bom: BillOfMaterials) -> list[tuple[str, ...]]:
    """Tarjan SCCs, sorted for deterministic diagnostic output."""
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    result: list[tuple[str, ...]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for child in bom.dependencies.get(node, ()):
            if child not in indices:
                visit(child)
                low[node] = min(low[node], low[child])
            elif child in on_stack:
                low[node] = min(low[node], indices[child])
        if low[node] == indices[node]:
            members = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                members.append(member)
                if member == node:
                    break
            result.append(tuple(sorted(members)))

    for node in sorted(bom.components):
        if node not in indices:
            visit(node)
    return sorted(result)
