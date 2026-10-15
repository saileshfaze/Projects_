"""Deterministic synthetic clicks, purchases and device telemetry."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import random

random.seed(2026)
base = datetime(2026, 10, 1, tzinfo=timezone.utc)
destination = Path(__file__).resolve().parents[1] / "data/synthetic_events.jsonl"
destination.parent.mkdir(exist_ok=True)
with destination.open("w", encoding="utf-8") as stream:
    for i in range(240):
        event_type = ("click", "purchase", "telemetry")[i % 3]
        attributes = {
            "click": {"page": f"/product/{i % 7}", "session_id": f"session-{i // 3}"},
            "purchase": {"order_id": f"order-{i}", "currency": "EUR"},
            "telemetry": {"device_id": f"sensor-{i % 4}"},
        }[event_type]
        record = {
            "event_id": f"evt-{i:05d}",
            "event_type": event_type,
            "occurred_at": (base + timedelta(minutes=i * 4)).isoformat(),
            "value": round(random.uniform(1, 20), 2),
            "schema_version": 1,
            "attributes": attributes,
        }
        stream.write(json.dumps(record, sort_keys=True) + "\n")
print(f"Generated {destination} (240 records)")
