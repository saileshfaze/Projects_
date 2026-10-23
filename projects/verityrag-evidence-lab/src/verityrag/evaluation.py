"""Offline ranking metrics, segment reporting, and deterministic bootstrap intervals."""
from __future__ import annotations

from collections import defaultdict
import math
import random
from .retrieval import HybridIndex


def ranking_metrics(ids: list[str], relevant: set[str], k: int) -> dict[str, float]:
    top = ids[:k]
    hits = [1 if item in relevant else 0 for item in top]
    recall = sum(hits) / len(relevant) if relevant else 0.0
    precision = sum(hits) / k
    mrr = next((1 / (i + 1) for i, h in enumerate(hits) if h), 0.0)
    dcg = sum(h / math.log2(i + 2) for i, h in enumerate(hits))
    ideal = sum(1 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return {"recall": recall, "precision": precision, "mrr": mrr,
            "ndcg": dcg / ideal if ideal else 0.0}


def bootstrap_ci(values: list[float], seed: int = 42, repetitions: int = 500) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n
                   for _ in range(repetitions))
    return [round(means[int(.025 * (repetitions - 1))], 4),
            round(means[int(.975 * (repetitions - 1))], 4)]


def evaluate(index: HybridIndex, questions: list[dict], qrels: dict[str, set[str]],
             k: int = 5) -> dict:
    if not questions:
        raise ValueError("evaluation requires questions")
    rows = []
    segments = defaultdict(list)
    for question in questions:
        qid = question["id"]
        hits = index.search(question["question"], k)
        metrics = ranking_metrics([h.document.id for h in hits], qrels.get(qid, set()), k)
        row = {"id": qid, "slice": question.get("slice", "general"), **metrics,
               "retrieved": [h.document.id for h in hits]}
        rows.append(row)
        segments[row["slice"]].append(row)
    keys = ("recall", "precision", "mrr", "ndcg")

    def aggregate(group):
        return {key: round(sum(r[key] for r in group) / len(group), 4)
                for key in keys}

    return {"k": k, "queries": len(rows), "overall": aggregate(rows),
            "confidence_intervals": {key: bootstrap_ci([r[key] for r in rows]) for key in keys},
            "slices": {s: {"queries": len(group), **aggregate(group)}
                       for s, group in sorted(segments.items())}, "per_query": rows}
