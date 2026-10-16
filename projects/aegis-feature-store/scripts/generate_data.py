"""Generate deterministic synthetic features and prediction observations.

No external data or personally identifiable information is used.
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import random


def generate(output: Path, seed: int = 42, entities: int = 50, days: int = 40):
    rng = random.Random(seed)
    output.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events, labels = [], []
    for day in range(days):
        for entity in range(entities):
            event_time = start + timedelta(days=day, hours=8)
            available = event_time + timedelta(minutes=rng.choice([1, 5, 30, 180]))
            score = round(rng.random(), 5)
            count = rng.randrange(0, 20)
            active = rng.random() > 0.2
            events.append({
                "event_id": f"synthetic-{day:03d}-{entity:04d}",
                "entity_key": f"entity-{entity:04d}",
                "event_ts": event_time.isoformat(),
                "available_ts": available.isoformat(),
                "values": {"score": score, "count": count, "active": active},
            })
            if day >= 2:
                label_time = event_time + timedelta(hours=2)
                # Synthetic target: correlated with features but not a real-world label.
                probability = min(0.95, 0.05 + 0.65 * score + 0.01 * count)
                labels.append({
                    "entity_key": f"entity-{entity:04d}",
                    "as_of": label_time.isoformat(),
                    "label": int(rng.random() < probability),
                })
    (output / "events.json").write_text(json.dumps(events, indent=2) + "\n")
    (output / "labels.json").write_text(json.dumps(labels, indent=2) + "\n")
    print(f"Generated {len(events)} feature events and {len(labels)} labels in {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--entities", type=int, default=50)
    parser.add_argument("--days", type=int, default=40)
    args = parser.parse_args()
    generate(args.output, args.seed, args.entities, args.days)


if __name__ == "__main__":
    main()
