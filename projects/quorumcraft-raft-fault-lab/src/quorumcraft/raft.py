"""Deterministic Raft core: elections, log replication, crash and partition faults.

This is a discrete-event educational simulator, not a production Raft implementation.
It intentionally omits joint consensus, snapshots, pre-vote and disk durability.
"""
from __future__ import annotations
import random
from typing import Any
from .model import Node, Entry
from .network import Network, Packet
from .audit import AuditChain
from .invariants import check_safety


class Cluster:
    def __init__(self, size: int = 5, seed: int = 42, latency: tuple[int, int] = (1, 2),
                 loss: float = 0.0, election_range: tuple[int, int] = (8, 14), heartbeat: int = 2):
        if size < 3 or size % 2 == 0:
            raise ValueError("cluster size must be an odd number of at least three")
        if election_range[0] <= heartbeat * 2 or election_range[1] < election_range[0]:
            raise ValueError("election timeouts must exceed two heartbeat intervals")
        self.seed = seed
        self.rng = random.Random(seed)
        self.network = Network(seed + 11, latency, loss)
        self.nodes = {f"n{i}": Node(f"n{i}") for i in range(1, size + 1)}
        self.now = 0
        self.heartbeat = heartbeat
        self.election_range = election_range
        self.audit = AuditChain()
        self.timeline: list[dict[str, Any]] = []
        self.commits: dict[str, int] = {}
        self._last_leader: str | None = None
        for node in self.nodes.values():
            self._reset_deadline(node)
        self.audit.append(0, "cluster_created", {"nodes": list(self.nodes), "seed": seed})

    @property
    def quorum(self) -> int:
        return len(self.nodes) // 2 + 1

    def _reset_deadline(self, node: Node) -> None:
        node.election_deadline = self.now + self.rng.randint(*self.election_range)

    def _step_down(self, node: Node, term: int) -> None:
        if term > node.current_term:
            node.current_term = term
            node.voted_for = None
        node.role = "follower"
        node.votes.clear()
        node.next_index.clear()
        node.match_index.clear()
        self._reset_deadline(node)

    def _broadcast(self, node: Node, kind: str, body: dict[str, Any]) -> None:
        for peer in self.nodes:
            if peer != node.node_id:
                self.network.send(self.now, node.node_id, peer, kind, node.current_term, body)

    def _start_election(self, node: Node) -> None:
        node.role = "candidate"
        node.current_term += 1
        node.voted_for = node.node_id
        node.votes = {node.node_id}
        self._reset_deadline(node)
        self.audit.append(self.now, "election_started", {"node": node.node_id, "term": node.current_term})
        self._broadcast(node, "vote_request", {"last_index": node.last_index, "last_term": node.last_term})

    def _become_leader(self, node: Node) -> None:
        node.role = "leader"
        node.next_index = {peer: node.last_index + 1 for peer in self.nodes if peer != node.node_id}
        node.match_index = {peer: 0 for peer in self.nodes if peer != node.node_id}
        node.match_index[node.node_id] = node.last_index
        node.heartbeat_deadline = self.now + self.heartbeat
        self.audit.append(self.now, "leader_elected", {"node": node.node_id, "term": node.current_term})
        for peer in node.next_index:
            self._send_append(node, peer)

    def _send_append(self, leader: Node, peer: str) -> None:
        next_index = max(1, leader.next_index[peer])
        prev_index = next_index - 1
        entries = [entry.to_dict() for entry in leader.log[next_index:]]
        self.network.send(self.now, leader.node_id, peer, "append_request", leader.current_term,
                          {"prev_index": prev_index, "prev_term": leader.log[prev_index].term,
                           "entries": entries, "leader_commit": leader.commit_index})

    def _advance_commit(self, leader: Node) -> None:
        for index in range(leader.last_index, leader.commit_index, -1):
            if leader.log[index].term != leader.current_term:
                continue
            replicated = 1 + sum(leader.match_index.get(peer, 0) >= index for peer in self.nodes if peer != leader.node_id)
            if replicated >= self.quorum:
                leader.commit_index = index
                self.audit.append(self.now, "committed", {"leader": leader.node_id, "index": index})
                for peer in leader.next_index:
                    self._send_append(leader, peer)
                break

    def _handle(self, packet: Packet) -> None:
        node = self.nodes[packet.receiver]
        if not node.active:
            return
        if packet.term > node.current_term:
            self._step_down(node, packet.term)
        if packet.kind == "vote_request":
            candidate_up_to_date = ((packet.body["last_term"], packet.body["last_index"]) >=
                                    (node.last_term, node.last_index))
            grant = (packet.term == node.current_term and
                     node.voted_for in (None, packet.sender) and candidate_up_to_date)
            if grant:
                node.voted_for = packet.sender
                self._reset_deadline(node)
            self.network.send(self.now, node.node_id, packet.sender, "vote_response", node.current_term,
                              {"granted": grant})
        elif packet.kind == "vote_response":
            if node.role != "candidate" or packet.term != node.current_term:
                return
            if packet.body["granted"]:
                node.votes.add(packet.sender)
                if len(node.votes) >= self.quorum:
                    self._become_leader(node)
        elif packet.kind == "append_request":
            if packet.term < node.current_term:
                self._append_reply(node, packet.sender, False, 0)
                return
            if node.role != "follower":
                self._step_down(node, packet.term)
            self._reset_deadline(node)
            prev = packet.body["prev_index"]
            if prev > node.last_index or node.log[prev].term != packet.body["prev_term"]:
                self._append_reply(node, packet.sender, False, 0)
                return
            for raw in packet.body["entries"]:
                entry = Entry(**raw)
                if entry.index <= node.last_index and node.log[entry.index] != entry:
                    if entry.index <= node.commit_index:
                        raise RuntimeError("attempt to overwrite committed entry")
                    node.log = node.log[:entry.index]
                if entry.index > node.last_index:
                    node.log.append(entry)
            node.commit_index = min(packet.body["leader_commit"], node.last_index) if packet.body["leader_commit"] > node.commit_index else node.commit_index
            self._apply(node)
            match = prev + len(packet.body["entries"])
            self._append_reply(node, packet.sender, True, match)
        elif packet.kind == "append_response":
            if node.role != "leader" or packet.term != node.current_term:
                return
            if packet.body["success"]:
                match = packet.body["match"]
                node.match_index[packet.sender] = max(node.match_index.get(packet.sender, 0), match)
                node.next_index[packet.sender] = node.match_index[packet.sender] + 1
                self._advance_commit(node)
            else:
                node.next_index[packet.sender] = max(1, node.next_index.get(packet.sender, 1) - 1)
                self._send_append(node, packet.sender)

    def _append_reply(self, node: Node, leader: str, success: bool, match: int) -> None:
        self.network.send(self.now, node.node_id, leader, "append_response", node.current_term,
                          {"success": success, "match": match})

    def _apply(self, node: Node) -> None:
        while node.last_applied < node.commit_index:
            node.last_applied += 1
            entry = node.log[node.last_applied]
            if entry.request_id in node.applied_requests:
                continue
            op = entry.command["op"]
            key = entry.command["key"]
            if op == "put":
                node.state[key] = entry.command["value"]
            elif op == "delete":
                node.state.pop(key, None)
            elif op == "increment":
                node.state[key] = int(node.state.get(key, 0)) + int(entry.command["value"])
            else:
                raise ValueError(f"unsupported operation: {op}")
            node.applied_requests.add(entry.request_id)
            self.commits.setdefault(entry.request_id, self.now)

    def leader(self) -> Node | None:
        leaders = [n for n in self.nodes.values() if n.active and n.role == "leader"]
        return leaders[0] if len(leaders) == 1 else None

    def submit(self, command: dict[str, Any], request_id: str) -> int | None:
        if not request_id or not isinstance(request_id, str):
            raise ValueError("request_id must be a non-empty string")
        if command.get("op") not in {"put", "delete", "increment"} or not isinstance(command.get("key"), str) or not command["key"]:
            raise ValueError("invalid command operation or key")
        if command["op"] in {"put", "increment"} and "value" not in command:
            raise ValueError("missing value")
        if command["op"] == "increment" and (isinstance(command["value"], bool) or not isinstance(command["value"], int)):
            raise ValueError("increment value must be an integer")
        leader = self.leader()
        if leader is None:
            return None
        for entry in leader.log[1:]:
            if entry.request_id == request_id:
                return entry.index
        index = leader.last_index + 1
        leader.log.append(Entry(leader.current_term, index, request_id, dict(command)))
        leader.match_index[leader.node_id] = index
        self.audit.append(self.now, "client_accepted", {"leader": leader.node_id, "index": index, "request_id": request_id})
        for peer in leader.next_index:
            self._send_append(leader, peer)
        return index

    def crash(self, node_id: str) -> None:
        node = self.nodes[node_id]
        node.active = False
        node.role = "follower"
        self.audit.append(self.now, "crash", {"node": node_id})

    def recover(self, node_id: str) -> None:
        node = self.nodes[node_id]
        node.active = True
        node.role = "follower"
        self._reset_deadline(node)
        self.audit.append(self.now, "recover", {"node": node_id})

    def partition(self, group_a: list[str], group_b: list[str]) -> None:
        if any(n not in self.nodes for n in group_a + group_b):
            raise ValueError("unknown node")
        self.network.partition(group_a, group_b)
        self.audit.append(self.now, "partition", {"a": group_a, "b": group_b})

    def heal(self) -> None:
        self.network.heal()
        self.audit.append(self.now, "heal", {})

    def tick(self, steps: int = 1, validate: bool = True) -> None:
        if steps < 0:
            raise ValueError("steps must be non-negative")
        for _ in range(steps):
            self.now += 1
            active = {n.node_id for n in self.nodes.values() if n.active}
            for packet in self.network.receive(self.now, active):
                self._handle(packet)
            for node in self.nodes.values():
                if not node.active:
                    continue
                if node.role == "leader" and self.now >= node.heartbeat_deadline:
                    node.heartbeat_deadline = self.now + self.heartbeat
                    for peer in node.next_index:
                        self._send_append(node, peer)
                elif node.role != "leader" and self.now >= node.election_deadline:
                    self._start_election(node)
                self._apply(node)
            if validate:
                check_safety(self.nodes)
            current = self.leader()
            leader_id = current.node_id if current else None
            if leader_id != self._last_leader:
                self._last_leader = leader_id
            self.timeline.append({"tick": self.now, "leader": leader_id,
                                  "committed": max(n.commit_index for n in self.nodes.values()),
                                  "active": len(active), "blocked_links": len(self.network.blocked)})

    def summary(self) -> dict[str, Any]:
        return {"tick": self.now, "quorum": self.quorum,
                "leader": self.leader().node_id if self.leader() else None,
                "nodes": [n.summary() for n in self.nodes.values()],
                "network": self.network.stats(), "audit_valid": self.audit.verify(),
                "events": len(self.audit.records)}
