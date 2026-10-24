"""Synthetic correlated preperiod and experiment outcomes for demonstrations."""
from __future__ import annotations
import csv
import random
from pathlib import Path
from .assignment import arm
from .models import Experiment, Outcome


def generate(config: Experiment, n: int = 800, seed: int = 42, lift: float = 0.08) -> list[Outcome]:
    if n < 2 or n > 100_000:
        raise ValueError("n must be between 2 and 100000")
    rng = random.Random(seed)
    events = []
    for i in range(n):
        user = f"user-{i:06d}"
        treatment = arm(config,user) == "B"
        latent = rng.gauss(0,1)
        preperiod = max(0, 24 + 8*latent + rng.gauss(0,4))
        converted = rng.random() < min(0.95, max(0.02,0.34+0.05*latent+(lift if treatment else 0)))
        revenue = round(max(0, (19 + 6*latent + rng.gauss(0,5))*(1+lift*int(treatment))),2) if converted else 0.0
        refunded = converted and rng.random() < (0.07 + 0.01*int(treatment))
        events.append(Outcome(f"event-{i:06d}",config.experiment_id,user,revenue,round(preperiod,2),converted,refunded,"2026-10-01T12:00:00+00:00"))
    return events


def write_csv(events: list[Outcome], path: str | Path) -> None:
    from dataclasses import asdict
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=list(asdict(events[0])))
        writer.writeheader()
        for event in events:
            writer.writerow(asdict(event))


def read_csv(path: str | Path) -> list[Outcome]:
    with open(path,newline="",encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [Outcome(r["event_id"],r["experiment_id"],r["subject_id"],float(r["revenue"]),float(r["preperiod_revenue"]),r["converted"].lower()=="true",r["refunded"].lower()=="true",r["timestamp"]) for r in rows]
