"""Bounded content-defined chunking using a deterministic gear table."""
from __future__ import annotations
import hashlib

GEAR = [int.from_bytes(hashlib.sha256(bytes([i])).digest()[:8], "big") for i in range(256)]

def chunks(data: bytes, minimum: int = 2048, average: int = 8192, maximum: int = 32768):
    """Yield byte chunks. A rolling hash makes boundaries resistant to shifts."""
    if not (0 < minimum <= average <= maximum) or average & (average - 1):
        raise ValueError("average must be a power of two and min <= average <= max")
    start = 0
    rolling = 0
    for pos, value in enumerate(data):
        rolling = ((rolling << 1) + GEAR[value]) & ((1 << 64) - 1)
        size = pos + 1 - start
        if size >= maximum or (size >= minimum and (rolling & (average - 1)) == 0):
            yield data[start:pos + 1]
            start = pos + 1
            rolling = 0
    if start < len(data):
        yield data[start:]

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
