"""Deterministic demonstration traces; not measured energy or weather data."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from math import pi, sin
from random import Random
from dataclasses import asdict
import csv
import json
from pathlib import Path
from .models import Interval


def generate(days: int = 2, seed: int = 2026, outage_start: int | None = None, outage_length: int = 0, step_minutes: int = 15) -> list[Interval]:
    if not 1 <= days <= 31 or not 1 <= step_minutes <= 1440 or 1440 % step_minutes:
        raise ValueError("days must be 1..31 and step_minutes must divide a day")
    if outage_length < 0 or (outage_start is not None and outage_start < 0):
        raise ValueError("invalid outage range")
    rng = Random(seed)
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    n = days * 1440 // step_minutes
    result = []
    for i in range(n):
        ts = start + timedelta(minutes=i*step_minutes)
        hour = ts.hour + ts.minute/60
        daylight = max(0.0, sin(pi*(hour-6)/12))
        pv = max(0.0, 14*daylight*(0.75+0.2*rng.random()))
        morning = max(0.0, sin(pi*(hour-5)/5))
        evening = max(0.0, sin(pi*(hour-16)/7))
        load = max(0.5, 5.2 + 2.2*morning + 4.3*evening + rng.uniform(-0.55,0.55))
        peak = 17 <= hour < 21
        cheap = hour < 6
        price = 0.36 if peak else (0.11 if cheap else 0.23)
        price += rng.uniform(-0.015,0.015)
        outage = outage_start is not None and outage_start <= i < outage_start+outage_length
        result.append(Interval(ts.isoformat(), round(load,4), round(pv,4), round(price,4),
                               0.075, round(0.21 + (0.11 if peak else 0) + rng.uniform(0,0.025),4), not outage))
    return result


def save_json(profile: list[Interval], path: str | Path) -> None:
    Path(path).write_text(json.dumps([asdict(x) for x in profile], indent=2)+"\n", encoding="utf-8")


def load_json(path: str | Path) -> list[Interval]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("profile must be a JSON array")
    return [Interval(**row) for row in raw]


def save_csv(profile: list[Interval], path: str | Path) -> None:
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(profile[0])))
        writer.writeheader()
        writer.writerows(asdict(x) for x in profile)
