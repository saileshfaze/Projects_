import pytest
from queryweaver.parser import parse
from queryweaver.planner import optimize, naive_plan, explain, to_dot, PlanningError

SQL = "SELECT * FROM orders o JOIN customers c ON o.customer_id=c.id JOIN regions r ON c.region_id=r.id"


def operators(plan):
    return [plan.op] + [op for child in plan.children for op in operators(child)]


def test_cost_beats_naive(catalog):
    q = parse(SQL)
    assert optimize(q, catalog).cost <= naive_plan(q, catalog).cost


def test_explain(catalog):
    assert "cost=" in explain(optimize(parse(SQL), catalog))


def test_dot(catalog):
    assert "digraph" in to_dot(optimize(parse(SQL), catalog))


def test_join_operator(catalog):
    assert any("join" in x for x in operators(optimize(parse(SQL), catalog)))


def test_no_hash(catalog):
    assert "hash_join" not in operators(optimize(parse(SQL), catalog, allow_hash=False))


def test_disconnected(catalog):
    q = parse("SELECT * FROM customers c JOIN orders o ON c.id=o.customer_id JOIN regions r ON c.id=o.customer_id")
    with pytest.raises(PlanningError):
        optimize(q, catalog)


def test_cross_enabled(catalog):
    q = parse("SELECT * FROM customers c JOIN orders o ON c.id=o.customer_id JOIN regions r ON c.id=o.customer_id")
    assert optimize(q, catalog, allow_cross=True).rows > 0


def test_index_scan(catalog):
    q = parse("SELECT * FROM customers c WHERE c.id=1")
    assert optimize(q, catalog).op == "index_scan"


def test_limit_and_project(catalog):
    q = parse("SELECT c.id FROM customers c LIMIT 3")
    plan = optimize(q, catalog)
    assert plan.op == "limit" and plan.children[0].op == "project"


def test_determinism(catalog):
    q = parse(SQL)
    assert optimize(q, catalog).to_dict() == optimize(q, catalog).to_dict()


def test_plan_serializable(catalog):
    import json
    json.dumps(optimize(parse(SQL), catalog).to_dict())
