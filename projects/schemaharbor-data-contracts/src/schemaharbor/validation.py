"""Deterministic row-level contract validation and issue aggregation."""
from datetime import date
from .contracts import Contract

def check_value(field, value):
    if value is None or value == "":
        return None if field.nullable or not field.required else "missing"
    kind = field.kind
    try:
        if kind == "string":
            if not isinstance(value, str): return "type"
        elif kind == "boolean":
            if value not in ("true", "false", True, False): return "type"
        elif kind == "date":
            if not isinstance(value, str): return "type"
            date.fromisoformat(value)
        else:
            if isinstance(value, bool): return "type"
            n = float(value)
            if kind == "integer" and (not n.is_integer()): return "type"
            if field.minimum is not None and n < field.minimum: return "below_min"
            if field.maximum is not None and n > field.maximum: return "above_max"
    except (ValueError, TypeError, OverflowError):
        return "type"
    return None

def validate(contract: Contract, record: dict, strict_unknown=True):
    if not isinstance(record, dict): return [{"field": "*", "code": "not_object"}]
    issues = []
    for field in contract.fields:
        error = check_value(field, record.get(field.name))
        if error: issues.append({"field": field.name, "code": error})
    if strict_unknown:
        for key in sorted(record.keys() - {f.name for f in contract.fields}):
            issues.append({"field": key, "code": "unknown"})
    return issues

def profile(contract, records, strict_unknown=True):
    rows = list(records)
    findings = []
    counts = {}
    for index, record in enumerate(rows, start=1):
        issues = validate(contract, record, strict_unknown)
        if issues:
            findings.append({"row": index, "issues": issues})
            for issue in issues:
                key = issue["field"] + ":" + issue["code"]
                counts[key] = counts.get(key, 0) + 1
    return {"contract": contract.name, "version": contract.version, "rows": len(rows), "valid_rows": len(rows) - len(findings), "issue_counts": dict(sorted(counts.items())), "findings": findings}
