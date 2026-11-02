"""Deterministic, fictional document corpus for backup and deduplication demos."""
from pathlib import Path
import random

def generate(target: str | Path, seed=42, files=24):
    if files < 1: raise ValueError("files must be positive")
    rng = random.Random(seed)
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    common = "inventory,region,quantity,sku,day\n" + "SKU-0001,west,12,DEMO,2026-01-01\n" * 120
    for i in range(files):
        group = target / f"batch-{i // 8:02d}"
        group.mkdir(parents=True, exist_ok=True)
        noise = "".join(rng.choice("abcdef0123456789") for _ in range(200 + i * 3))
        (group / f"record-{i:03d}.csv").write_text(common + f"{i},synthetic,{noise}\n", encoding="utf-8")
    return files
