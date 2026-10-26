"""Normalize a strict, documented subset of CycloneDX and SPDX JSON."""
from __future__ import annotations
from collections import defaultdict
from typing import Any
from .models import BillOfMaterials, Component


class SBOMError(ValueError):
    """An input SBOM cannot be safely normalized."""


def _licenses(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    result = []
    for item in value:
        if not isinstance(item, dict):
            continue
        lic = item.get("license", item)
        if isinstance(lic, dict):
            name = lic.get("id") or lic.get("name")
            if isinstance(name, str) and name.strip():
                result.append(name.strip())
        elif isinstance(lic, str) and lic.strip():
            result.append(lic.strip())
    return tuple(sorted(set(result)))


def _finish(fmt: str, components: dict[str, Component], edges: dict[str, set[str]], roots: set[str]) -> BillOfMaterials:
    if not components:
        raise SBOMError("SBOM has no components")
    for parent, children in edges.items():
        if parent not in components:
            raise SBOMError(f"unknown dependency parent: {parent}")
        for child in children:
            if child not in components:
                raise SBOMError(f"unknown dependency target: {child}")
    if not roots:
        incoming = {child for children in edges.values() for child in children}
        roots = set(components) - incoming
        if not roots:  # A cyclic graph can have no zero-indegree node.
            roots = set(components)
    if roots - set(components):
        raise SBOMError("unknown root reference")
    return BillOfMaterials(fmt, components, {k: tuple(sorted(edges.get(k, ()))) for k in sorted(components)}, tuple(sorted(roots)))


def parse_cyclonedx(data: dict[str, Any]) -> BillOfMaterials:
    if data.get("bomFormat") != "CycloneDX":
        raise SBOMError("not a CycloneDX document")
    components: dict[str, Component] = {}
    for item in data.get("components", []):
        if not isinstance(item, dict):
            raise SBOMError("invalid component")
        ref = item.get("bom-ref") or item.get("purl")
        if not isinstance(ref, str) or not ref or ref in components:
            raise SBOMError("missing or duplicate bom-ref")
        components[ref] = Component(ref, str(item.get("name", "")), str(item.get("version", "")),
                                    str(item.get("purl", "")), _licenses(item.get("licenses")))
    edges: dict[str, set[str]] = defaultdict(set)
    for entry in data.get("dependencies", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("ref"), str):
            raise SBOMError("invalid dependency entry")
        edges[entry["ref"]].update(entry.get("dependsOn", []))
    meta = data.get("metadata") or {}
    root_ref = (meta.get("component") or {}).get("bom-ref") if isinstance(meta, dict) else None
    roots = {root_ref} if root_ref in components else set()
    return _finish("cyclonedx", components, edges, roots)


def parse_spdx(data: dict[str, Any]) -> BillOfMaterials:
    if "SPDXID" not in data or "packages" not in data:
        raise SBOMError("not an SPDX JSON document")
    components: dict[str, Component] = {}
    for item in data["packages"]:
        if not isinstance(item, dict):
            raise SBOMError("invalid SPDX package")
        ref = item.get("SPDXID")
        if not isinstance(ref, str) or not ref or ref in components:
            raise SBOMError("missing or duplicate SPDXID")
        purl = ""
        for external in item.get("externalRefs", []):
            if external.get("referenceType") == "purl":
                purl = str(external.get("referenceLocator", ""))
                break
        lic = str(item.get("licenseConcluded") or item.get("licenseDeclared") or "")
        licenses = () if lic in ("", "NOASSERTION", "NONE") else (lic,)
        components[ref] = Component(ref, str(item.get("name", "")), str(item.get("versionInfo", "")), purl, licenses)
    edges: dict[str, set[str]] = defaultdict(set)
    for rel in data.get("relationships", []):
        if rel.get("relationshipType") == "DEPENDS_ON":
            edges[rel["spdxElementId"]].add(rel["relatedSpdxElement"])
        elif rel.get("relationshipType") == "DEPENDENCY_OF":
            edges[rel["relatedSpdxElement"]].add(rel["spdxElementId"])
    roots = set(data.get("documentDescribes", [])) & set(components)
    return _finish("spdx", components, edges, roots)


def parse_sbom(data: dict[str, Any]) -> BillOfMaterials:
    if not isinstance(data, dict):
        raise SBOMError("SBOM must be a JSON object")
    if data.get("bomFormat") == "CycloneDX":
        return parse_cyclonedx(data)
    if "spdxVersion" in data:
        return parse_spdx(data)
    raise SBOMError("expected CycloneDX or SPDX JSON")
