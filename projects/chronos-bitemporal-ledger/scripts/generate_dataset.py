"""Generate reproducible fictional price-plan changes in JSON Lines format."""

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path


def generate(seed: int, tenants: int, entities: int, revisions: int) -> list[dict]:
    rng = random.Random(seed)
    records = []
    for tenant in range(tenants):
        for entity in range(entities):
            base = date(2026, 1, 1)
            for revision in range(revisions):
                start = base + timedelta(days=revision * 45)
                end = base + timedelta(days=365)
                records.append({
                    "tenant": f"tenant-{tenant:02d}",
                    "entity": f"plan-{entity:03d}",
                    "correction": {
                        "valid_from": start.isoformat(), "valid_to": end.isoformat(),
                        "payload": {
                            "monthly_eur": rng.randint(15, 200),
                            "tier": rng.choice(["basic", "pro", "enterprise"]),
                            "currency": "EUR", "revision": revision,
                        },
                        "actor": "synthetic-generator",
                        "idempotency_key": f"seed-{seed}-t{tenant}-e{entity}-r{revision}",
                    },
                })
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/generated_events.jsonl"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tenants", type=int, default=3)
    parser.add_argument("--entities", type=int, default=8)
    parser.add_argument("--revisions", type=int, default=4)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as out:
        for record in generate(args.seed, args.tenants, args.entities, args.revisions):
            out.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"Wrote {args.tenants * args.entities * args.revisions} fictional corrections")


if __name__ == "__main__":
    main()
