"""Deterministic binary classification metrics and population stability index."""

from bisect import bisect_right
from math import isfinite


def binary_metrics(actual: list[int], predicted: list[int]) -> dict[str, float]:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("Expected equally sized nonempty arrays")
    if any(x not in (0, 1) for x in actual + predicted):
        raise ValueError("Only binary labels 0 and 1 are supported")
    tp = sum(a == 1 and p == 1 for a, p in zip(actual, predicted))
    tn = sum(a == 0 and p == 0 for a, p in zip(actual, predicted))
    fp = sum(a == 0 and p == 1 for a, p in zip(actual, predicted))
    fn = sum(a == 1 and p == 0 for a, p in zip(actual, predicted))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "accuracy": (tp + tn) / len(actual),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def population_stability_index(
    reference: list[float], current: list[float], bins: int = 10, epsilon: float = 1e-6
) -> float:
    """Equal-width reference bins, Laplace-style epsilon smoothing; no data leakage."""
    if not reference or not current or bins < 2 or epsilon <= 0:
        raise ValueError("Invalid PSI input")
    if not all(isfinite(x) for x in reference + current):
        raise ValueError("PSI requires finite observations")
    lo, hi = min(reference), max(reference)
    if lo == hi:
        return 0.0 if all(x == lo for x in current) else float("inf")
    edges = [lo + (hi - lo) * i / bins for i in range(1, bins)]
    ref_counts = [0] * bins
    cur_counts = [0] * bins
    for x in reference:
        ref_counts[bisect_right(edges, x)] += 1
    for x in current:
        cur_counts[bisect_right(edges, x)] += 1
    from math import log

    psi = 0.0
    for a, b in zip(ref_counts, cur_counts):
        p = (a + epsilon) / (len(reference) + bins * epsilon)
        q = (b + epsilon) / (len(current) + bins * epsilon)
        psi += (q - p) * log(q / p)
    return max(0.0, psi)
