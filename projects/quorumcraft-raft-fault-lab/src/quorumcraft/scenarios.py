"""Reproducible fault scenarios and scripted event execution."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .raft import Cluster


@dataclass(frozen=True)
class Action:
    tick: int
    kind: str
    payload: dict[str, Any]


def run_scenario(cluster: Cluster, actions: list[Action], until: int) -> dict[str, Any]:
    if until < cluster.now:
        raise ValueError("until must be at or after current tick")
    if any(a.tick < cluster.now or a.tick > until for a in actions):
        raise ValueError("scenario action is outside the simulation interval")
    ordered = sorted(enumerate(actions), key=lambda x: (x[1].tick, x[0]))
    cursor = 0
    while cluster.now <= until:
        while cursor < len(ordered) and ordered[cursor][1].tick == cluster.now:
            action = ordered[cursor][1]
            if action.kind == "submit":
                cluster.submit(action.payload["command"], action.payload["request_id"])
            elif action.kind == "crash":
                cluster.crash(action.payload["node"])
            elif action.kind == "recover":
                cluster.recover(action.payload["node"])
            elif action.kind == "partition":
                cluster.partition(action.payload["a"], action.payload["b"])
            elif action.kind == "heal":
                cluster.heal()
            else:
                raise ValueError(f"unknown action: {action.kind}")
            cursor += 1
        if cluster.now == until:
            break
        cluster.tick()
    return cluster.summary()


def demo_actions() -> list[Action]:
    return [
        Action(35, "submit", {"request_id": "order-001", "command": {"op": "put", "key": "orders", "value": 10}}),
        Action(48, "submit", {"request_id": "order-002", "command": {"op": "increment", "key": "orders", "value": 3}}),
        Action(65, "partition", {"a": ["n1", "n2"], "b": ["n3", "n4", "n5"]}),
        Action(96, "heal", {}),
        Action(116, "submit", {"request_id": "order-003", "command": {"op": "increment", "key": "orders", "value": 2}}),
    ]


def actions_from_dict(data: list[dict[str, Any]]) -> list[Action]:
    return [Action(int(row["tick"]), str(row["kind"]), dict(row.get("payload", {}))) for row in data]
