import pytest
from queryweaver.parser import parse, tokenize, SQLSyntaxError

SQL = "SELECT c.id, o.id FROM customers c JOIN orders o ON c.id=o.customer_id WHERE c.age>=21 LIMIT 10"


def test_tokenizer():
    assert tokenize("SELECT a.id FROM abc a") == ["SELECT", "a", ".", "id", "FROM", "abc", "a"]


def test_query_shape():
    q = parse(SQL)
    assert len(q.columns) == 2 and len(q.relations) == 2
    assert q.relations[0].alias == "c" and q.limit == 10
    assert q.filters[0].right == 21


def test_star():
    assert parse("SELECT * FROM orders").columns is None


def test_alias_as():
    assert parse("SELECT * FROM orders AS o").relations[0].alias == "o"


def test_inner_join():
    assert len(parse("SELECT * FROM orders o INNER JOIN customers c ON o.customer_id=c.id").joins) == 1


def test_string_escaped():
    assert parse("SELECT * FROM orders o WHERE o.status='it''s paid'").filters[0].right == "it's paid"


def test_numeric():
    assert parse("SELECT * FROM products p WHERE p.price > 3.14").filters[0].right == 3.14


@pytest.mark.parametrize("sql", [
    "DELETE FROM orders", "SELECT * FROM", "SELECT * FROM orders; DROP TABLE orders",
    "SELECT * FROM orders o JOIN customers c ON o.id > c.id",
    "SELECT * FROM orders o WHERE o.id=1 OR o.id=2",
    "SELECT x.id FROM orders o", "SELECT * FROM orders o JOIN orders o ON o.id=o.id",
    "SELECT * FROM orders o WHERE o.id = o.id", "SELECT * FROM orders LIMIT -1",
    "SELECT * FROM orders LIMIT 100001", "SELECT * FROM orders WHERE x.id=1",
    "SELECT * FROM orders o JOIN orders p ON o.id=o.id",
    "SELECT * FROM orders o WHERE o.id = 1.2.3",
])
def test_invalid(sql):
    with pytest.raises(SQLSyntaxError):
        parse(sql)


def test_sql_length():
    with pytest.raises(SQLSyntaxError):
        parse(" " * 10001)
