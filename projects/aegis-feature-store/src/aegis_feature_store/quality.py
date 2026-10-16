"""Numerical distribution shift diagnostics for monitoring.

PSI is a heuristic monitoring signal, not a statistical significance test.
KS is the empirical two-sample statistic; no p-value is estimated here.
"""

from bisect import bisect_right
from math import isfinite, log


def _quantile(sorted_values: list[float], q: float) -> float:
    position = q * (len(sorted_values) - 1)
    lo = int(position)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (position - lo) * (sorted_values[hi] - sorted_values[lo])


def psi(reference: list[float], current: list[float], bins: int = 10) -> float:
    if len(reference) < 2 or len(current) < 2 or not 2 <= bins <= 50:
        raise ValueError("Two or more samples and 2-50 bins are required")
    if not all(isfinite(x) for x in reference + current):
        raise ValueError("Inputs must contain finite numbers")
    sorted_ref = sorted(reference)
    if sorted_ref[0] == sorted_ref[-1]:
        return 0.0 if all(x == sorted_ref[0] for x in current) else 10.0
    boundaries = sorted(set(_quantile(sorted_ref, i / bins) for i in range(1, bins)))
    n_bins = len(boundaries) + 1
    ref_counts = [0] * n_bins
    cur_counts = [0] * n_bins
    for value in reference:
        ref_counts[bisect_right(boundaries, value)] += 1
    for value in current:
        cur_counts[bisect_right(boundaries, value)] += 1
    smoothing = 1e-6
    score = 0.0
    for ref_count, cur_count in zip(ref_counts, cur_counts):
        ref_p = max(ref_count / len(reference), smoothing)
        cur_p = max(cur_count / len(current), smoothing)
        score += (cur_p - ref_p) * log(cur_p / ref_p)
    return round(score, 8)


def ks_statistic(reference: list[float], current: list[float]) -> float:
    if not reference or not current:
        raise ValueError("Both distributions must be nonempty")
    if not all(isfinite(x) for x in reference + current):
        raise ValueError("Inputs must contain finite numbers")
    a, b = sorted(reference), sorted(current)
    i = j = 0
    maximum = 0.0
    for value in sorted(set(a + b)):
        while i < len(a) and a[i] <= value:
            i += 1
        while j < len(b) and b[j] <= value:
            j += 1
        maximum = max(maximum, abs(i / len(a) - j / len(b)))
    return round(maximum, 8)


def drift_report(reference: list[float], current: list[float], bins: int = 10) -> dict:
    score = psi(reference, current, bins)
    return {
        "reference_count": len(reference),
        "current_count": len(current),
        "psi": score,
        "ks_statistic": ks_statistic(reference, current),
        "psi_signal": "investigate" if score >= 0.2 else "stable",
        "note": "Threshold is heuristic; interpret with feature context and sample size.",
    }
