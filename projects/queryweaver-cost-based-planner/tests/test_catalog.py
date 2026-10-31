import pytest
from queryweaver.catalog import Catalog, CatalogError, ColumnStats, TableStats, from_rows
from queryweaver.parser import parse


def test_stats(catalog):
    assert catalog.tables["orders"].rows == 80
    assert catalog.tables["orders"].columns["customer_id"].indexed


def test_eq_selectivity(catalog):
    q = parse("SELECT * FROM customers c WHERE c.age=21")
    assert 0 < catalog.selectivity(q.filters[0], q) <= 1


def test_range_selectivity(catalog):
    q = parse("SELECT * FROM customers c WHERE c.age>40")
    assert 0 < catalog.selectivity(q.filters[0], q) < 1


def test_unknown_table(catalog):
    with pytest.raises(CatalogError):
        catalog.validate(parse("SELECT * FROM nonexistent x"))


def test_unknown_column(catalog):
    with pytest.raises(CatalogError):
        catalog.validate(parse("SELECT * FROM customers c WHERE c.missing=1"))


def test_negative_rows():
    with pytest.raises(CatalogError):
        Catalog({"x": TableStats(-1, {})})


def test_zero_distinct():
    with pytest.raises(CatalogError):
        Catalog({"x": TableStats(1, {"id": ColumnStats(0)})})


def test_empty_table():
    assert from_rows({"empty": []}).tables["empty"].rows == 0
