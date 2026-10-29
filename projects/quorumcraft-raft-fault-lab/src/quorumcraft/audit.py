"""Tamper-evident, deterministic audit chain for simulated events."""
from __future__ import annotations
import hashlib
import json
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class AuditChain:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def append(self, tick: int, action: str, details: dict[str, Any]) -> dict[str, Any]:
        previous = self.records[-1]["hash"] if self.records else "0" * 64
        payload = {"seq": len(self.records) + 1, "tick": tick, "action": action,
                   "details": details, "previous": previous}
        record = {**payload, "hash": hashlib.sha256(canonical(payload).encode()).hexdigest()}
        self.records.append(record)
        return record

    def verify(self) -> bool:
        previous = "0" * 64
        for seq, record in enumerate(self.records, 1):
            payload = {key: record[key] for key in ("seq", "tick", "action", "details", "previous")}
            if record["seq"] != seq or record["previous"] != previous:
                return False
            if hashlib.sha256(canonical(payload).encode()).hexdigest() != record["hash"]:
                return False
            previous = record["hash"]
        return True
