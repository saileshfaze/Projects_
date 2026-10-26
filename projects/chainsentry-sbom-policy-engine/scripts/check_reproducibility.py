"""Confirm fixture and SVG generators are byte-for-byte deterministic."""
import hashlib
from pathlib import Path
from generate_fixtures import generate
from render_architecture import render

root = Path(__file__).resolve().parents[1]
paths = sorted((root / "examples").glob("*.json")) + [root / "assets" / "architecture.svg"]

def digests():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

before = digests()
generate()
render()
after = digests()
assert before == after, "reproducibility check failed"
print(f"Verified {len(after)} deterministic generated assets")
