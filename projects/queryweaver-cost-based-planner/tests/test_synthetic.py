import pytest
from queryweaver.synthetic import generate, save, load


def test_deterministic():
    assert generate(123) == generate(123)


def test_seeds_differ():
    assert generate(1) != generate(2)


def test_referential_integrity():
    data = generate(customers=3, products=2, orders=10)
    assert all(1 <= r["customer_id"] <= 3 and 1 <= r["product_id"] <= 2 for r in data["orders"])


def test_csv_roundtrip(tmp_path):
    data = generate(customers=5, products=3, orders=10)
    counts = save(data, tmp_path)
    assert counts["orders"] == 10
    assert load(tmp_path) == data


def test_reject_bad_dimensions():
    with pytest.raises(ValueError):
        generate(customers=0)


def test_reject_excessive_dimensions():
    with pytest.raises(ValueError):
        generate(orders=100001)
