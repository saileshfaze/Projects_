"""Transparent two-arm experiment statistics; not a causal inference guarantee."""
from __future__ import annotations
import math
import random
from statistics import mean
from typing import Sequence


def srm_test(a: int, b: int, treatment_fraction: float) -> dict:
    """Two-cell Pearson chi-square with exact chi-square(1) survival function."""
    n = a + b
    if n == 0:
        return {"chi_square": None, "p_value": None, "flag": False}
    ea, eb = n * (1 - treatment_fraction), n * treatment_fraction
    chi = (a-ea)**2 / ea + (b-eb)**2 / eb
    p = math.erfc(math.sqrt(chi / 2))
    return {"chi_square": chi, "p_value": p, "flag": p < 0.001}


def cuped(a: Sequence[dict], b: Sequence[dict]) -> tuple[list[float], list[float], float]:
    """Estimate a single pooled preperiod coefficient, avoiding arm-specific centering."""
    rows = list(a) + list(b)
    if not rows:
        return [], [], 0.0
    x = [float(r["preperiod_revenue"]) for r in rows]
    y = [float(r["revenue"]) for r in rows]
    mx, my = mean(x), mean(y)
    vx = sum((v-mx)**2 for v in x)
    theta = sum((u-mx)*(v-my) for u,v in zip(x,y))/vx if vx > 1e-12 else 0.0
    def adjusted(group: Sequence[dict]) -> list[float]:
        return [float(r["revenue"]) - theta*(float(r["preperiod_revenue"])-mx) for r in group]
    return adjusted(a), adjusted(b), theta


def bootstrap_difference(a: Sequence[float], b: Sequence[float], alpha: float, seed: int = 17, draws: int = 1200) -> dict:
    if len(a) < 2 or len(b) < 2:
        return {"difference": None, "ci_low": None, "ci_high": None, "draws": 0}
    rng = random.Random(seed)
    delta = mean(b) - mean(a)
    n_a, n_b = len(a), len(b)
    sims = []
    for _ in range(draws):
        sims.append(sum(a[rng.randrange(n_a)] for _ in range(n_a))/n_a)
        sims[-1] = sum(b[rng.randrange(n_b)] for _ in range(n_b))/n_b - sims[-1]
    sims.sort()
    lo = sims[max(0, min(draws-1, int(draws*alpha/2)))]
    hi = sims[max(0, min(draws-1, int(draws*(1-alpha/2))-1))]
    return {"difference": delta, "ci_low": lo, "ci_high": hi, "draws": draws}


def analyze(rows: list[dict], assigned: dict[str,int], treatment_fraction: float, alpha: float = 0.05, planned_looks: int = 1, minimum_per_arm: int = 20, seed: int = 17) -> dict:
    arms = {key: [r for r in rows if r["arm"] == key] for key in ("A", "B")}
    a,b = arms["A"], arms["B"]
    n_a,n_b = len(a),len(b)
    spent_alpha = alpha / planned_looks
    result = {
        "assigned": assigned, "observed": {"A":n_a,"B":n_b},
        "srm": srm_test(assigned["A"],assigned["B"],treatment_fraction),
        "alpha_per_look":spent_alpha,
        "eligible": min(n_a,n_b)>=minimum_per_arm,
        "missing_outcome_rate": {k: (1-len(arms[k])/assigned[k]) if assigned[k] else None for k in arms},
        "warnings": [],
    }
    if result["srm"]["flag"]:
        result["warnings"].append("Sample ratio mismatch: investigate assignment/instrumentation")
    if any(v is not None and v > 0.05 for v in result["missing_outcome_rate"].values()):
        result["warnings"].append("More than 5% of assigned subjects lack an outcome")
    if not result["eligible"]:
        result["warnings"].append("Insufficient observations: do not interpret intervals as decision-ready")
    adj_a,adj_b,theta = cuped(a,b)
    result["cuped_theta"] = theta
    for metric, vals_a, vals_b in (
        ("revenue", [r["revenue"] for r in a],[r["revenue"] for r in b]),
        ("revenue_cuped", adj_a,adj_b),
        ("conversion", [r["converted"] for r in a],[r["converted"] for r in b]),
        ("refund_guardrail", [r["refunded"] for r in a],[r["refunded"] for r in b]),
    ):
        result[metric] = {
            "mean_A":mean(vals_a) if vals_a else None,
            "mean_B":mean(vals_b) if vals_b else None,
            **bootstrap_difference(vals_a, vals_b, spent_alpha, seed=seed),
        }
    result["interpretation"] = "Exploratory bootstrap intervals; pre-register stopping, metrics, and analysis plan before production use"
    return result
