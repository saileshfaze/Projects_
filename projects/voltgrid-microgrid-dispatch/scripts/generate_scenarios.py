"""Deterministically regenerate the committed synthetic JSON/CSV/forecast history."""
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
start = datetime(2026, 10, 1, tzinfo=timezone.utc)

def load(hour):
    return 4 + (4 if 17 <= hour <= 21 else 0) + (2 if 8 <= hour <= 16 else 0)

slots = []
for h in range(24):
    slots.append({
        "timestamp": (start + timedelta(hours=h)).isoformat(),
        "load_kw": load(h),
        "solar_kw": max(0, 8 - abs(h - 12) * 2),
        "import_price_usd_per_kwh": 0.12 if h < 7 else (0.35 if 17 <= h <= 21 else 0.20),
        "export_price_usd_per_kwh": 0.05,
        "grid_kgco2_per_kwh": 0.36,
    })
scenario = {
    "name": "synthetic-office-solar-battery-2026-10-01",
    "currency": "USD",
    "interval_minutes": 60,
    "slots": slots,
    "battery": {
        "capacity_kwh": 16, "initial_soc_kwh": 8, "min_soc_kwh": 2,
        "target_final_soc_kwh": 8, "max_charge_kw": 6, "max_discharge_kw": 6,
        "charge_efficiency": 0.95, "discharge_efficiency": 0.95,
        "degradation_usd_per_kwh": 0.005,
    },
    "grid": {
        "max_import_kw": 30, "max_export_kw": 10,
        "demand_charge_usd_per_kw": 1.5, "carbon_price_usd_per_kg": 0.05,
    },
}
(DATA / "demo_scenario.json").write_text(json.dumps(scenario, indent=2) + "\n")
with (DATA / "demo_intervals.csv").open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(slots[0]))
    writer.writeheader()
    writer.writerows(slots)
history = [load(h % 24) + (h // 24) % 3 for h in range(72)]
(DATA / "historical_load.json").write_text(json.dumps(history, indent=2) + "\n")
print("Generated synthetic scenario, interval CSV and load history.")
