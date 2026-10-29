"""Data types for the deterministic Raft teaching simulator."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Entry:
    term: int
    index: int
    request_id: str
    command: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"term": self.term, "index": self.index, "request_id": self.request_id, "command": self.command}


@dataclass
class Node:
    node_id: str
    current_term: int = 0
    voted_for: str | None = None
    role: str = "follower"
    log: list[Entry] = field(default_factory=lambda: [Entry(0, 0, "genesis", {})])
    commit_index: int = 0
    last_applied: int = 0
    election_deadline: int = 0
    heartbeat_deadline: int = 0
    active: bool = True
    votes: set[str] = field(default_factory=set)
    next_index: dict[str, int] = field(default_factory=dict)
    match_index: dict[str, int] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    applied_requests: set[str] = field(default_factory=set)

    @property
    def last_index(self) -> int:
        return len(self.log) - 1

    @property
    def last_term(self) -> int:
        return self.log[-1].term

    def summary(self) -> dict[str, Any]:
        return {"id": self.node_id, "term": self.current_term, "role": self.role,
                "active": self.active, "last_index": self.last_index,
                "commit_index": self.commit_index, "state": dict(self.state)}
