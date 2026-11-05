import math
import random
import pytest
from privacylens.core import PrivacyLedger, bound_contributions, laplace, private_histogram, private_mean

def test_ledger_composition():
    ledger = PrivacyLedger(1)
    ledger.consume(.4, "a")
    ledger.consume(.6, "b")
    assert ledger.spent == 1
    assert len(ledger.entries) == 2

def test_budget_rejected():
    ledger = PrivacyLedger(1)
    ledger.consume(.8, "first")
    with pytest.raises(ValueError): ledger.consume(.3, "second")
    assert ledger.spent == .8

@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf")])
def test_invalid_budget(bad):
    with pytest.raises(ValueError): PrivacyLedger(bad)

@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf")])
def test_invalid_epsilon(bad):
    with pytest.raises(ValueError): PrivacyLedger(1).consume(bad, "x")

def test_contribution_bound():
    rows = [{"u": "a", "v": i} for i in range(4)] + [{"u": "b", "v": 9}]
    assert len(bound_contributions(rows, "u", 1)) == 2
    assert len(bound_contributions(rows, "u", 2)) == 3

def test_invalid_cap():
    with pytest.raises(ValueError): bound_contributions([], "u", 0)

def test_histogram_seed_reproducible():
    rows = [{"c": "x"}, {"c": "x"}, {"c": "y"}]
    a = private_histogram(rows, "c", ["x", "y"], 1, PrivacyLedger(1), random.Random(3))
    b = private_histogram(rows, "c", ["x", "y"], 1, PrivacyLedger(1), random.Random(3))
    assert a == b

def test_histogram_categories_validation():
    with pytest.raises(ValueError): private_histogram([], "c", ["x", "x"], 1, PrivacyLedger(1), random.Random(1))

def test_mean_bounded():
    ledger = PrivacyLedger(1)
    value = private_mean([{"v": -100}, {"v": 100}], "v", 0, 10, 1, ledger, random.Random(2), 2)
    assert math.isfinite(value)
    assert ledger.spent == 1

def test_mean_requires_public_count():
    with pytest.raises(ValueError): private_mean([{"v": 2}], "v", 0, 10, 1, PrivacyLedger(1), random.Random(1), 2)

def test_laplace_finite():
    assert all(math.isfinite(laplace(1, random.Random(i))) for i in range(100))

def test_noise_distribution():
    rng = random.Random(123)
    draws = [laplace(2, rng) for _ in range(10000)]
    assert abs(sum(draws) / len(draws)) < .15
