"""Immutable domain types used by the normalization and evaluation pipeline."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(frozen=True)
class Component:
    ref: str
    name: str
    version: str
    purl: str
    licenses: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"licenses": list(self.licenses)}


@dataclass(frozen=True)
class BillOfMaterials:
    format: str
    components: dict[str, Component]
    dependencies: dict[str, tuple[str, ...]]
    roots: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"format": self.format, "components": {k: v.to_dict() for k, v in sorted(self.components.items())},
                "dependencies": {k: list(v) for k, v in sorted(self.dependencies.items())}, "roots": list(self.roots)}


@dataclass(frozen=True)
class Advisory:
    id: str
    purl_name: str
    introduced: str
    fixed: str | None
    severity: str
    summary: str = ""


@dataclass(frozen=True)
class Finding:
    kind: str
    rule: str
    component: str
    severity: str
    message: str
    reachable: bool
    exempted: bool = False
    advisory: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Report:
    digest: str
    status: str
    format: str
    total_components: int
    reachable_components: int
    findings: tuple[Finding, ...]
    summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"digest": self.digest, "status": self.status, "format": self.format,
                "total_components": self.total_components, "reachable_components": self.reachable_components,
                "summary": self.summary, "findings": [f.to_dict() for f in self.findings]}
