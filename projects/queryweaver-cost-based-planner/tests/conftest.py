import pytest
from queryweaver.synthetic import generate
from queryweaver.catalog import from_rows


@pytest.fixture
def tables():
    return generate(seed=31, customers=15, orders=80, products=9)


@pytest.fixture
def catalog(tables):
    return from_rows(tables, {"orders": {"id", "customer_id", "product_id"},
                              "customers": {"id"}, "products": {"id"}, "regions": {"id"}})
