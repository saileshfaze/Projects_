"""Availability and convergence metrics for deterministic experiments."""
from __future__ import annotations
from collections import Counter
from typing import Any
from .raft import Cluster


def evaluate(cluster: Cluster) -> dict[str, Any]:
    timeline = cluster.timeline
    observed = len(timeline)
    with_leader = sum(1 for point in timeline if point["leader"] is not None)
    transitions = sum(1 for i in range(1, observed)
                      if timeline[i]["leader"] != timeline[i - 1]["leader"]
                      and timeline[i]["leader"] is not None)
    leaders = Counter(point["leader"] for point in timeline if point["leader"])
    return {"ticks": observed,
            "leader_available_fraction": round(with_leader / observed, 4) if observed else 0.0,
            "leadership_transitions": transitions,
            "leader_tick_counts": dict(sorted(leaders.items())),
            "max_committed_index": max((n.commit_index for n in cluster.nodes.values()), default=0),
            "network": cluster.network.stats(),
            "audit_events": len(cluster.audit.records),
            "audit_valid": cluster.audit.verify()}
