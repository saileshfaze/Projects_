import pytest
from queryweaver.diagnostics import inspect, InvalidPlan
from queryweaver.model import Plan
from queryweaver.parser import parse
from queryweaver.planner import optimize


def test_summary(catalog):
    query = parse("SELECT * FROM customers c JOIN orders o ON c.id=o.customer_id")
    summary = inspect(optimize(query, catalog), query)
    assert summary.scan_aliases == ("c", "o")
    assert summary.depth >= 2
    assert summary.to_dict()["estimated_cost"] > 0


def test_unknown_operator():
    with pytest.raises(InvalidPlan):
        inspect(Plan("delete", ("c",), 1, 1), parse("SELECT * FROM customers c"))


def test_missing_alias():
    with pytest.raises(InvalidPlan):
        inspect(Plan("table_scan", ("x",), 1, 1), parse("SELECT * FROM customers c"))


def test_negative_cost():
    with pytest.raises(InvalidPlan):
        inspect(Plan("table_scan", ("c",), 1, -1), parse("SELECT * FROM customers c"))


def test_invalid_scan_children():
    child = Plan("table_scan", ("c",), 1, 1)
    with pytest.raises(InvalidPlan):
        inspect(Plan("table_scan", ("c",), 1, 1, children=(child,)), parse("SELECT * FROM customers c"))
