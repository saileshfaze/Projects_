"""Typed intermediate representation for a deliberately constrained SQL dialect."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

Scalar = int | float | str | bool | None


@dataclass(frozen=True)
class Column:
    table: str
    name: str

    def __str__(self) -> str:
        return f"{self.table}.{self.name}"


@dataclass(frozen=True)
class Predicate:
    left: Column
    op: str
    right: Column | Scalar


@dataclass(frozen=True)
class Relation:
    name: str
    alias: str


@dataclass(frozen=True)
class Query:
    columns: tuple[Column, ...] | None
    relations: tuple[Relation, ...]
    joins: tuple[Predicate, ...]
    filters: tuple[Predicate, ...]
    limit: int | None = None


@dataclass
class Plan:
    op: str
    tables: tuple[str, ...]
    rows: float
    cost: float
    detail: dict[str, Any] = field(default_factory=dict)
    children: tuple[Plan, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"op": self.op, "tables": list(self.tables), "rows": round(self.rows, 4),
                "cost": round(self.cost, 4), "detail": self.detail,
                "children": [x.to_dict() for x in self.children]}
