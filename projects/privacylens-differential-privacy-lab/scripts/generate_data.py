"""Generate deterministic fictional records only."""
import csv
import random
from pathlib import Path

def generate(path: Path, n=300, seed=2026):
    rng = random.Random(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "region", "spend"])
        writer.writeheader()
        for i in range(n):
            writer.writerow({"user_id": f"synthetic-{i:04d}",
                             "region": rng.choice(["north", "south", "west"]),
                             "spend": round(rng.uniform(5, 100), 2)})
if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "data" / "synthetic_users.csv")
