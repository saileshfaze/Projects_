"""Infer response shapes and classify consumer-facing contract changes."""
from functools import reduce


def kind(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    raise TypeError("Value is not JSON compatible")


def shape(value):
    t = kind(value)
    if t == "object":
        return {"type": t, "properties": {k: shape(v) for k, v in sorted(value.items())}, "required": sorted(value)}
    if t == "array":
        return {"type": t, "items": infer(value) if value else {"type": "unknown"}}
    return {"type": t}


def types(schema):
    value = schema["type"]
    return set(value if isinstance(value, list) else [value])


def merge(left, right):
    if left["type"] == "unknown":
        return right
    if right["type"] == "unknown":
        return left
    union = types(left) | types(right)
    if union == {"array"}:
        return {"type": "array", "items": merge(left["items"], right["items"])}
    if union == {"object"}:
        a, b = left["properties"], right["properties"]
        return {
            "type": "object",
            "properties": {
                k: merge(a[k], b[k]) if k in a and k in b else a.get(k, b.get(k))
                for k in sorted(a.keys() | b.keys())
            },
            "required": sorted(set(left["required"]) & set(right["required"])),
        }
    return {"type": sorted(union)[0] if len(union) == 1 else sorted(union)}


def infer(samples):
    if not samples:
        raise ValueError("At least one sample is required")
    return reduce(merge, map(shape, samples))


def changes(baseline, candidate):
    findings = []

    def add(severity, code, path, detail):
        findings.append({"severity": severity, "code": code, "path": path, "detail": detail})

    def visit(old, new, path):
        before, after = types(old), types(new)
        if "unknown" in before or "unknown" in after:
            return
        accepted = before | ({"integer"} if "number" in before else set())
        if not after <= accepted:
            add("breaking", "TYPE_WIDENED", path, f"{sorted(before)} -> {sorted(after)}")
        elif before != after:
            add("info", "TYPE_NARROWED", path, f"{sorted(before)} -> {sorted(after)}")
        if before == {"object"} and after == {"object"}:
            a, b = old["properties"], new["properties"]
            required_old, required_new = set(old["required"]), set(new["required"])
            for key in sorted(a.keys() - b.keys()):
                add("breaking" if key in required_old else "warning", "FIELD_REMOVED", f"{path}.{key}", "Field disappeared")
            for key in sorted(a.keys() & b.keys()):
                if key in required_old and key not in required_new:
                    add("breaking", "FIELD_BECAME_OPTIONAL", f"{path}.{key}", "Required field became optional")
                visit(a[key], b[key], f"{path}.{key}")
            for key in sorted(b.keys() - a.keys()):
                add("info", "FIELD_ADDED", f"{path}.{key}", "New field")
        if before == {"array"} and after == {"array"}:
            visit(old["items"], new["items"], f"{path}[]")

    visit(baseline, candidate, "$")
    return findings
