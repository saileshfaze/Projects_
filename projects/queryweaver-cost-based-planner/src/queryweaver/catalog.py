"""Column statistics and schema validation for cost estimation."""
from __future__ import annotations
from dataclasses import dataclass
from .model import Column, Query


class CatalogError(ValueError):
    pass


@dataclass(frozen=True)
class ColumnStats:
    distinct: int
    minimum: float | None = None
    maximum: float | None = None
    indexed: bool = False


@dataclass(frozen=True)
class TableStats:
    rows: int
    columns: dict[str, ColumnStats]


class Catalog:
    def __init__(self, tables: dict[str, TableStats]):
        self.tables = tables
        for name, table in tables.items():
            if table.rows < 0:
                raise CatalogError(f"Negative row count for {name}")
            for col, stat in table.columns.items():
                if stat.distinct < 1:
                    raise CatalogError(f"Invalid distinct count for {name}.{col}")

    def column(self, column: Column, query: Query) -> ColumnStats:
        relation = next((r for r in query.relations if r.alias == column.table), None)
        if relation is None or relation.name not in self.tables:
            raise CatalogError(f"Unknown table: {column.table}")
        table = self.tables[relation.name]
        if column.name not in table.columns:
            raise CatalogError(f"Unknown column: {column}")
        return table.columns[column.name]

    def validate(self, query: Query) -> None:
        for relation in query.relations:
            if relation.name not in self.tables:
                raise CatalogError(f"Unknown relation {relation.name}")
        for column in (query.columns or ()):
            self.column(column, query)
        for predicate in (*query.filters, *query.joins):
            self.column(predicate.left, query)
            if isinstance(predicate.right, Column):
                self.column(predicate.right, query)

    def selectivity(self, predicate, query: Query) -> float:
        left = self.column(predicate.left, query)
        if isinstance(predicate.right, Column):
            right = self.column(predicate.right, query)
            return max(1e-6, 1.0 / max(left.distinct, right.distinct))
        if predicate.op == "=":
            return 1.0 / left.distinct
        if predicate.op == "!=":
            return 1.0 - 1.0 / left.distinct
        if predicate.op in {"<", ">", "<=", ">="}:
            if isinstance(predicate.right, (int, float)) and left.minimum is not None and left.maximum is not None:
                span = left.maximum - left.minimum
                if span <= 0:
                    return 0.5
                fraction = max(0.0, min(1.0, (predicate.right - left.minimum) / span))
                return fraction if predicate.op in {"<", "<="} else 1 - fraction
            return 0.3333
        return 0.5


def from_rows(tables: dict[str, list[dict]], indexed: dict[str, set[str]] | None = None) -> Catalog:
    indexed = indexed or {}
    result = {}
    for name, rows in tables.items():
        columns = set().union(*(row.keys() for row in rows)) if rows else set()
        stats = {}
        for column in columns:
            values = [row[column] for row in rows if row.get(column) is not None]
            numeric = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
            stats[column] = ColumnStats(max(1, len(set(values))),
                                        min(numeric) if numeric and len(numeric) == len(values) else None,
                                        max(numeric) if numeric and len(numeric) == len(values) else None,
                                        column in indexed.get(name, set()))
        result[name] = TableStats(len(rows), stats)
    return Catalog(result)
