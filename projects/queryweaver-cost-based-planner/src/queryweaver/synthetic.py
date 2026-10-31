"""Deterministic star-schema fixture generator and reproducible data export."""
from __future__ import annotations
import csv
import json
import random
from pathlib import Path


def generate(seed: int = 2026, customers: int = 120, orders: int = 900,
             products: int = 40) -> dict[str, list[dict]]:
    if min(customers, orders, products) < 1:
        raise ValueError("Fixture dimensions must be positive")
    if max(customers, orders, products) > 100000:
        raise ValueError("Fixture dimensions exceed safety limit")
    rng = random.Random(seed)
    regions = [{"id": i, "name": name, "tax_rate": rate} for i, (name, rate) in
               enumerate([("north", 0.19), ("south", 0.18), ("east", 0.21), ("west", 0.20)], start=1)]
    customer_rows = [{"id": i, "region_id": rng.randint(1, 4),
                      "tier": rng.choice(["standard", "standard", "premium"]),
                      "age": rng.randint(18, 79)} for i in range(1, customers + 1)]
    product_rows = [{"id": i, "category": rng.choice(["tools", "home", "tech", "sports"]),
                     "price": rng.randint(5, 300)} for i in range(1, products + 1)]
    order_rows = [{"id": i, "customer_id": rng.randint(1, customers),
                   "product_id": rng.randint(1, products),
                   "quantity": rng.randint(1, 5),
                   "status": rng.choice(["paid", "paid", "paid", "pending", "returned"])}
                  for i in range(1, orders + 1)]
    return {"regions": regions, "customers": customer_rows, "products": product_rows, "orders": order_rows}


def save(tables: dict[str, list[dict]], destination: Path) -> dict[str, int]:
    destination.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, rows in sorted(tables.items()):
        if not rows:
            continue
        with (destination / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        counts[name] = len(rows)
    (destination / "manifest.json").write_text(json.dumps({"tables": counts}, indent=2) + "\n")
    return counts


def load(destination: Path) -> dict[str, list[dict]]:
    tables = {}
    for path in sorted(destination.glob("*.csv")):
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            tables[path.stem] = [{k: (int(v) if v.isdecimal() else float(v) if v.replace(".", "", 1).isdecimal() else v)
                                  for k, v in row.items()} for row in reader]
    return tables
