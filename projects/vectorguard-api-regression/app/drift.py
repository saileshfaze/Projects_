"""Offline drift metrics; no external model or credentials required."""
import math
import re
from bisect import bisect_right
from collections import Counter


def _finite(values):
    if not values or any(not math.isfinite(float(v)) for v in values):
        raise ValueError("Expected a nonempty list of finite numeric values")
    return sorted(float(v) for v in values)


def population_stability_index(baseline, candidate, bins=10):
    """PSI on baseline quantile bins with additive smoothing."""
    a, b = _finite(baseline), _finite(candidate)
    if bins < 2:
        raise ValueError("bins must be >= 2")
    edges = sorted(set(a[min(len(a) - 1, int(len(a) * i / bins))] for i in range(1, bins)))
    count = len(edges) + 1

    def histogram(values):
        counts = [0] * count
        for value in values:
            counts[bisect_right(edges, value)] += 1
        return counts

    old, new = histogram(a), histogram(b)
    eps = 0.0001
    left = [(v / len(a) + eps) / (1 + count * eps) for v in old]
    right = [(v / len(b) + eps) / (1 + count * eps) for v in new]
    return round(sum((y - x) * math.log(y / x) for x, y in zip(left, right)), 6)


def ks_distance(baseline, candidate):
    a, b = _finite(baseline), _finite(candidate)
    return round(max(
        abs(bisect_right(a, x) / len(a) - bisect_right(b, x) / len(b))
        for x in sorted(set(a + b))
    ), 6)


def lexical_similarity(left, right):
    """Token and bigram cosine similarity; this is not an embedding score."""
    def vector(text):
        words = re.findall(r"[a-z0-9]+", text.casefold())
        return Counter(words + [f"{a}_{b}" for a, b in zip(words, words[1:])])
    a, b = vector(left), vector(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(key, 0) for key, value in a.items())
    return round(dot / math.sqrt(
        sum(v * v for v in a.values()) * sum(v * v for v in b.values())
    ), 6)


def drift_summary(baseline, candidate, psi_limit=0.2, ks_limit=0.3):
    if psi_limit < 0 or not 0 <= ks_limit <= 1:
        raise ValueError("Invalid drift thresholds")
    psi = population_stability_index(baseline, candidate)
    ks = ks_distance(baseline, candidate)
    return {
        "baseline_count": len(baseline),
        "candidate_count": len(candidate),
        "psi": psi,
        "ks_distance": ks,
        "drift_detected": psi >= psi_limit or ks >= ks_limit,
        "thresholds": {"psi": psi_limit, "ks_distance": ks_limit},
    }
