"""Backward compatibility: can a new consumer accept every old valid record?"""
from dataclasses import dataclass, asdict
from .contracts import Contract

@dataclass(frozen=True)
class Change:
    field: str
    severity: str
    code: str
    explanation: str

    def to_dict(self):
        return asdict(self)

def compare(old: Contract, new: Contract) -> list[Change]:
    if old.name != new.name:
        raise ValueError("different contract names")
    a = {f.name: f for f in old.fields}
    b = {f.name: f for f in new.fields}
    out = []
    def add(name, severity, code, why):
        out.append(Change(name, severity, code, why))
    for name in sorted(a.keys() - b.keys()):
        add(name, "breaking", "removed", "previously accepted field removed")
    for name in sorted(b.keys() - a.keys()):
        add(name, "breaking" if b[name].required else "compatible", "added", "new required field" if b[name].required else "new optional field")
    for name in sorted(a.keys() & b.keys()):
        x, y = a[name], b[name]
        if x.kind != y.kind:
            if x.kind == "integer" and y.kind == "number":
                add(name, "compatible", "widened_type", "integer widened to number")
            else:
                add(name, "breaking", "type_changed", f"{x.kind} to {y.kind}")
        if not x.required and y.required:
            add(name, "breaking", "required", "optional field became required")
        if x.required and not y.required:
            add(name, "compatible", "optional", "required field became optional")
        if x.nullable and not y.nullable:
            add(name, "breaking", "non_nullable", "null is no longer accepted")
        if not x.nullable and y.nullable:
            add(name, "compatible", "nullable", "null is now accepted")
        if y.minimum is not None and (x.minimum is None or y.minimum > x.minimum):
            add(name, "breaking", "min_tightened", "lower bound tightened")
        elif x.minimum is not None and (y.minimum is None or y.minimum < x.minimum):
            add(name, "compatible", "min_relaxed", "lower bound relaxed")
        if y.maximum is not None and (x.maximum is None or y.maximum < x.maximum):
            add(name, "breaking", "max_tightened", "upper bound tightened")
        elif x.maximum is not None and (y.maximum is None or y.maximum > x.maximum):
            add(name, "compatible", "max_relaxed", "upper bound relaxed")
    return out

def recommendation(changes):
    if any(c.severity == "breaking" for c in changes):
        return "major"
    if changes:
        return "minor"
    return "patch"
