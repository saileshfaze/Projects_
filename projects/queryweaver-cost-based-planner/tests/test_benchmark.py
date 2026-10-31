import pytest
from queryweaver.benchmark import benchmark


def test_benchmark_equivalence():
    result = benchmark(seed=5, repetitions=1, customers=12, orders=45, products=6)
    assert len(result) == 3
    assert all(row["equivalent"] for row in result)
    assert all(row["optimized_estimated_cost"] <= row["baseline_estimated_cost"] for row in result)


def test_reject_repetitions():
    with pytest.raises(ValueError):
        benchmark(repetitions=0)
