"""Deterministic, non-sensitive binary-classification dataset."""

import csv
import random
from pathlib import Path


def make_rows(count: int = 320, seed: int = 2026) -> list[dict]:
    if count < 20:
        raise ValueError("Generate at least 20 rows")
    rng = random.Random(seed)
    rows = []
    for index in range(count):
        age = rng.randint(18, 72)
        usage_hours = round(rng.uniform(0, 30), 2)
        incidents = rng.randint(0, 7)
        score = 0.16 * usage_hours + 0.65 * incidents + 0.015 * age + rng.gauss(0, 0.6)
        label = int(score > 5.1)
        rows.append({"customer_id": f"SYN-{index:05d}", "age": age,
                     "usage_hours": usage_hours, "incidents": incidents, "label": label})
    return rows


def write_csv(path: str | Path, rows: list[dict]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
