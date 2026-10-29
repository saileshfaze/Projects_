"""Safety checks: elected leader uniqueness and committed-prefix agreement."""
from __future__ import annotations
from .model import Node


class SafetyViolation(AssertionError):
    pass


def check_safety(nodes: dict[str, Node]) -> dict[str, int]:
    active_leaders: dict[int, str] = {}
    for node in nodes.values():
        if node.active and node.role == "leader":
            prior = active_leaders.get(node.current_term)
            if prior and prior != node.node_id:
                raise SafetyViolation(f"two active leaders in term {node.current_term}: {prior}, {node.node_id}")
            active_leaders[node.current_term] = node.node_id
        if node.commit_index > node.last_index or node.last_applied > node.commit_index:
            raise SafetyViolation(f"invalid commit/application index on {node.node_id}")
        if any(entry.index != idx for idx, entry in enumerate(node.log)):
            raise SafetyViolation(f"noncontiguous log on {node.node_id}")
    values = list(nodes.values())
    checked = 0
    for i, left in enumerate(values):
        for right in values[i + 1:]:
            common = min(left.commit_index, right.commit_index)
            for index in range(1, common + 1):
                if left.log[index] != right.log[index]:
                    raise SafetyViolation(f"committed divergence at {index}: {left.node_id}/{right.node_id}")
                checked += 1
            if left.last_applied == right.last_applied and left.state != right.state:
                raise SafetyViolation(f"state machine divergence: {left.node_id}/{right.node_id}")
    return {"active_leaders": len(active_leaders), "committed_pairs_checked": checked}
