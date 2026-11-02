"""Canonical JSON manifest and digest verification."""
import json
from .chunking import sha256
from .errors import IntegrityError

def canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

def seal(payload: dict) -> dict:
    return {**payload, "digest": sha256(canonical(payload))}

def verify(manifest: dict) -> None:
    expected = manifest.get("digest")
    if not isinstance(expected, str) or sha256(canonical({k:v for k,v in manifest.items() if k != "digest"})) != expected:
        raise IntegrityError("manifest checksum mismatch")
