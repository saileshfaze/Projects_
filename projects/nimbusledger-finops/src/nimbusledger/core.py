"""Pure FinOps calculations; amounts are represented as Decimal."""
from collections import defaultdict
from decimal import Decimal
from statistics import median


def allocate(amount: Decimal, weights: dict[str, Decimal]) -> dict[str, Decimal]:
    if amount < 0 or not weights or any(w < 0 for w in weights.values()):
        raise ValueError('Invalid allocation inputs')
    total = sum(weights.values(), Decimal('0'))
    if total <= 0:
        raise ValueError('Weights must be positive')
    keys = sorted(weights)
    result = {k: (amount * weights[k] / total).quantize(Decimal('0.01')) for k in keys[:-1]}
    result[keys[-1]] = amount - sum(result.values(), Decimal('0'))
    return result


def summarize(records: list[dict]) -> dict[str, Decimal]:
    totals = defaultdict(lambda: Decimal('0'))
    for row in records:
        totals[row['service']] += Decimal(str(row['cost']))
    return dict(sorted(totals.items()))


def anomaly_scores(values: list[float]) -> list[float]:
    if not values:
        return []
    center = median(values)
    mad = median(abs(x - center) for x in values)
    if mad == 0:
        return [0.0 if x == center else float('inf') for x in values]
    return [0.6745 * (x - center) / mad for x in values]


def budget_remaining(budget: Decimal, spent: Decimal) -> Decimal:
    return budget - spent
