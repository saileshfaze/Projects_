"""Median absolute deviation (MAD) scores by event type."""
from collections import defaultdict
from statistics import median


def robust_scores(values: list[float]) -> list[float]:
    if not values:
        return []
    center = median(values)
    mad = median(abs(value - center) for value in values)
    if mad == 0:
        return [0.0 if value == center else 999.0 for value in values]
    return [round(0.6745 * (value - center) / mad, 4) for value in values]


def score_windows(rows: list[dict], threshold: float = 3.5) -> list[dict]:
    """Compare observed window counts within each event type, not across types."""
    groups: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[row["event_type"]].append((index, float(row["count"])))
    scores = [0.0] * len(rows)
    for group in groups.values():
        computed = robust_scores([value for _, value in group])
        for (index, _), score in zip(group, computed):
            scores[index] = score
    return [
        {**row, "score": scores[index], "anomalous": abs(scores[index]) >= threshold}
        for index, row in enumerate(rows)
    ]
