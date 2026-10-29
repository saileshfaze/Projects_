"""Seeded, event-driven transport with bidirectional network partitions."""
from __future__ import annotations
import heapq
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class Packet:
    due: int
    sequence: int
    sender: str = field(compare=False)
    receiver: str = field(compare=False)
    kind: str = field(compare=False)
    term: int = field(compare=False)
    body: dict[str, Any] = field(compare=False)


class Network:
    def __init__(self, seed: int = 42, latency: tuple[int, int] = (1, 2), loss: float = 0.0):
        if latency[0] < 1 or latency[1] < latency[0]:
            raise ValueError("latency must be a positive, ordered interval")
        if not 0 <= loss <= 1:
            raise ValueError("loss must be between zero and one")
        self.rng = random.Random(seed)
        self.latency = latency
        self.loss = loss
        self.blocked: set[frozenset[str]] = set()
        self.queue: list[Packet] = []
        self.sequence = 0
        self.sent = 0
        self.delivered = 0
        self.dropped = 0

    def partition(self, group_a: list[str], group_b: list[str]) -> None:
        for a in group_a:
            for b in group_b:
                if a != b:
                    self.blocked.add(frozenset((a, b)))

    def heal(self) -> None:
        self.blocked.clear()

    def allowed(self, sender: str, receiver: str) -> bool:
        return frozenset((sender, receiver)) not in self.blocked

    def send(self, now: int, sender: str, receiver: str, kind: str, term: int, body: dict[str, Any]) -> None:
        self.sent += 1
        if not self.allowed(sender, receiver) or self.rng.random() < self.loss:
            self.dropped += 1
            return
        self.sequence += 1
        heapq.heappush(self.queue, Packet(now + self.rng.randint(*self.latency),
                                          self.sequence, sender, receiver, kind, term, body))

    def receive(self, now: int, active: set[str]) -> list[Packet]:
        ready = []
        while self.queue and self.queue[0].due <= now:
            packet = heapq.heappop(self.queue)
            if not self.allowed(packet.sender, packet.receiver) or packet.receiver not in active or packet.sender not in active:
                self.dropped += 1
            else:
                self.delivered += 1
                ready.append(packet)
        return ready

    def stats(self) -> dict[str, int]:
        return {"sent": self.sent, "delivered": self.delivered, "dropped": self.dropped,
                "in_flight": len(self.queue), "blocked_links": len(self.blocked)}
