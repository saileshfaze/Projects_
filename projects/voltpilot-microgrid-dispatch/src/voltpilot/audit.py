"""Tamper-evident hash chain for each simulated interval."""
import hashlib
import json
from dataclasses import asdict
from .models import Dispatch


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def chain(steps: list[Dispatch]) -> list[dict]:
    prev = "0"*64
    output = []
    for index, step in enumerate(steps):
        payload = asdict(step)
        digest = hashlib.sha256(prev.encode("ascii") + canonical(payload)).hexdigest()
        output.append({"index": index, "previous_hash": prev, "hash": digest, "step": payload})
        prev = digest
    return output


def verify(entries: list[dict]) -> bool:
    prev = "0"*64
    for index, row in enumerate(entries):
        if row.get("index") != index or row.get("previous_hash") != prev:
            return False
        payload = row.get("step")
        if not isinstance(payload, dict):
            return False
        expected = hashlib.sha256(prev.encode("ascii") + canonical(payload)).hexdigest()
        if row.get("hash") != expected:
            return False
        prev = expected
    return True
