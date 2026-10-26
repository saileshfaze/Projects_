"""Policy evaluation; findings remain visible even when a VEX exemption applies."""
from __future__ import annotations
from datetime import date
from hashlib import sha256
import json
from typing import Any
from .models import BillOfMaterials, Finding, Report
from .advisories import load_feed, matches, SEVERITIES
from .graph import shortest_paths


class PolicyError(ValueError):
    pass


def canonical_digest(bom: BillOfMaterials) -> str:
    payload = json.dumps(bom.to_dict(), sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode()).hexdigest()


def _validate(policy: dict[str, Any]) -> None:
    if not isinstance(policy, dict):
        raise PolicyError("policy must be an object")
    if policy.get("fail_at", "high") not in SEVERITIES:
        raise PolicyError("invalid fail_at severity")
    if not isinstance(policy.get("deny_licenses", []), list):
        raise PolicyError("deny_licenses must be a list")
    if not isinstance(policy.get("exemptions", []), list):
        raise PolicyError("exemptions must be a list")


def _exempt(advisory: str, purl: str, policy: dict[str, Any], today: date) -> bool:
    for item in policy.get("exemptions", []):
        if not isinstance(item, dict):
            raise PolicyError("invalid exemption")
        if not item.get("justification"):
            raise PolicyError("exemption requires justification")
        try:
            expiry = date.fromisoformat(item["expires"])
        except (KeyError, ValueError, TypeError) as exc:
            raise PolicyError("exemption requires ISO expiry date") from exc
        if item.get("advisory") == advisory and item.get("purl") == purl and expiry >= today:
            return True
    return False


def evaluate(bom: BillOfMaterials, feed: dict[str, Any], policy: dict[str, Any], today: date | None = None) -> Report:
    _validate(policy)
    today = today or date.today()
    paths = shortest_paths(bom)
    advisories = load_feed(feed)
    findings: list[Finding] = []
    denied = {str(v).lower() for v in policy.get("deny_licenses", [])}
    for ref, comp in sorted(bom.components.items()):
        reachable = ref in paths
        for adv in advisories:
            if matches(comp, adv):
                exempted = _exempt(adv.id, comp.purl, policy, today)
                findings.append(Finding("vulnerability", "advisory-match", ref, adv.severity,
                                        f"{adv.id}: {adv.summary}".strip(), reachable, exempted, adv.id))
        for license_id in comp.licenses:
            if license_id.lower() in denied:
                findings.append(Finding("license", "denied-license", ref, "high", f"Denied license: {license_id}", reachable))
        if not comp.licenses and policy.get("require_license", False):
            findings.append(Finding("license", "missing-license", ref, "medium", "No declared license", reachable))
        if not comp.purl and policy.get("require_purl", False):
            findings.append(Finding("metadata", "missing-purl", ref, "medium", "No package URL", reachable))
    findings.sort(key=lambda f: (f.component, f.kind, f.rule, f.advisory or ""))
    threshold = SEVERITIES[policy.get("fail_at", "high")]
    # All components are evaluated, including unreachable nodes; unreachable findings are informational unless configured.
    failed = any(SEVERITIES[f.severity] >= threshold and not f.exempted and
                 (f.reachable or policy.get("fail_unreachable", False)) for f in findings)
    summary = {"total": len(findings), "active": sum(not f.exempted for f in findings),
               "exempted": sum(f.exempted for f in findings),
               "unreachable": sum(not f.reachable for f in findings)}
    return Report(canonical_digest(bom), "fail" if failed else "pass", bom.format, len(bom.components),
                  len(paths), tuple(findings), summary)
