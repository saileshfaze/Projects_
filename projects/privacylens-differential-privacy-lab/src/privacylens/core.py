"""Differential privacy mechanisms for bounded synthetic analytics.

The ledger uses basic sequential composition, not advanced accounting.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import Iterable


def laplace(scale: float, rng: random.Random) -> float:
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("scale must be finite and positive")
    u = rng.random() - 0.5
    return -scale * math.copysign(math.log1p(-2 * abs(u)), u)


@dataclass
class PrivacyLedger:
    epsilon_limit: float
    spent: float = 0.0
    entries: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not math.isfinite(self.epsilon_limit) or self.epsilon_limit <= 0:
            raise ValueError("epsilon_limit must be positive and finite")

    def consume(self, epsilon: float, label: str):
        if not math.isfinite(epsilon) or epsilon <= 0:
            raise ValueError("epsilon must be positive and finite")
        if self.spent + epsilon > self.epsilon_limit + 1e-12:
            raise ValueError("privacy budget exhausted")
        self.spent += epsilon
        self.entries.append({"label": label, "epsilon": epsilon, "cumulative": self.spent})

    def report(self):
        return {"epsilon_limit": self.epsilon_limit, "spent": self.spent,
                "remaining": max(0., self.epsilon_limit - self.spent), "queries": self.entries}


def bound_contributions(rows: Iterable[dict], user_key: str, cap: int = 1) -> list[dict]:
    if cap < 1:
        raise ValueError("cap must be >= 1")
    counts: dict[str, int] = {}
    output = []
    for row in rows:
        user = str(row[user_key])
        if counts.get(user, 0) < cap:
            output.append(dict(row))
            counts[user] = counts.get(user, 0) + 1
    return output


def private_histogram(rows: Iterable[dict], key: str, categories: list[str], epsilon: float,
                      ledger: PrivacyLedger, rng: random.Random) -> dict[str, float]:
    if not categories or len(set(categories)) != len(categories):
        raise ValueError("categories must be nonempty and unique")
    if not math.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be positive")
    ledger.consume(epsilon, f"histogram:{key}")
    counts = {c: 0 for c in categories}
    for row in rows:
        category = str(row.get(key, ""))
        if category in counts:
            counts[category] += 1
    return {c: counts[c] + laplace(1 / epsilon, rng) for c in categories}


def private_mean(rows: Iterable[dict], key: str, lower: float, upper: float,
                 epsilon: float, ledger: PrivacyLedger, rng: random.Random,
                 public_count: int) -> float:
    if not all(math.isfinite(v) for v in (lower, upper)) or lower >= upper:
        raise ValueError("invalid clipping bounds")
    if not isinstance(public_count, int) or public_count <= 0:
        raise ValueError("public_count must be positive integer")
    if not math.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be positive")
    values = [min(upper, max(lower, float(r[key]))) for r in rows]
    if len(values) != public_count:
        raise ValueError("public_count must match bounded input size; count must not be inferred privately")
    ledger.consume(epsilon, f"mean:{key}")
    return (sum(values) + laplace((upper - lower) / epsilon, rng)) / public_count
