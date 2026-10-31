import pytest
from queryweaver.parser import parse
from queryweaver.planner import optimize, naive_plan
from queryweaver.engine import execute, canonical, ExecutionError

QUERIES = [
    "SELECT * FROM customers c",
    "SELECT c.id FROM customers c WHERE c.age>=40",
    "SELECT * FROM orders o WHERE o.status='paid'",
    "SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id",
    "SELECT c.id, o.id FROM orders o JOIN customers c ON o.customer_id=c.id WHERE c.age>30",
    "SELECT * FROM orders o JOIN products p ON o.product_id=p.id WHERE p.price>80",
    "SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id JOIN regions r ON c.region_id=r.id",
    "SELECT * FROM orders o JOIN products p ON o.product_id=p.id JOIN customers c ON o.customer_id=c.id",
    "SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id JOIN regions r ON c.region_id=r.id JOIN products p ON o.product_id=p.id",
    "SELECT * FROM orders o WHERE o.id=100000",
    "SELECT * FROM customers c WHERE c.age != 30",
]


@pytest.mark.parametrize("sql", QUERIES)
def test_equivalence(sql, catalog, tables):
    q = parse(sql)
    fast, _ = execute(optimize(q, catalog), q, tables)
    slow, _ = execute(naive_plan(q, catalog), q, tables)
    assert canonical(fast) == canonical(slow)


def test_limit(catalog, tables):
    q = parse("SELECT c.id FROM customers c LIMIT 3")
    result, _ = execute(optimize(q, catalog), q, tables)
    assert len(result) == 3 and list(result[0]) == ["c.id"]


def test_stats(catalog, tables):
    q = parse("SELECT * FROM customers c")
    result, stats = execute(optimize(q, catalog), q, tables)
    assert stats.scanned == len(result) == 15


def test_null_predicate(catalog, tables):
    tables["customers"][0]["age"] = None
    q = parse("SELECT * FROM customers c WHERE c.age>20")
    rows, _ = execute(optimize(q, catalog), q, tables)
    assert len(rows) <= 14


def test_missing_column(catalog, tables):
    del tables["customers"][0]["age"]
    q = parse("SELECT * FROM customers c WHERE c.age>20")
    with pytest.raises(ExecutionError):
        execute(optimize(q, catalog), q, tables)


def test_row_cap(catalog, tables):
    q = parse("SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id")
    with pytest.raises(ExecutionError):
        execute(optimize(q, catalog), q, tables, max_rows=2)
