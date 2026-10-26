"""Offline advisory feed and deterministic version interval matching."""
from __future__ import annotations
from typing import Any
from packaging.version import Version, InvalidVersion
from .models import Advisory, Component

SEVERITIES = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


class FeedError(ValueError):
    pass


def purl_package(purl: str) -> str:
    """Normalize package coordinates, retaining ecosystem and namespace.

    Qualifiers/subpaths are excluded; the version is taken from Component.version.
    """
    if not purl.startswith("pkg:"):
        return ""
    raw = purl[4:].split("?", 1)[0].split("#", 1)[0].split("@", 1)[0]
    return raw.lower().rstrip("/")


def load_feed(data: Any) -> tuple[Advisory, ...]:
    if not isinstance(data, dict) or not isinstance(data.get("advisories"), list):
        raise FeedError("advisory feed requires advisories list")
    result = []
    seen = set()
    for row in data["advisories"]:
        try:
            adv = Advisory(id=str(row["id"]), purl_name=str(row["purl_name"]).lower(),
                           introduced=str(row.get("introduced", "0")),
                           fixed=str(row["fixed"]) if row.get("fixed") is not None else None,
                           severity=str(row["severity"]).lower(), summary=str(row.get("summary", "")))
            if not adv.id or not adv.purl_name or adv.severity not in SEVERITIES:
                raise ValueError("invalid advisory")
            Version(adv.introduced)
            if adv.fixed is not None and Version(adv.fixed) <= Version(adv.introduced):
                raise ValueError("fixed must exceed introduced")
        except (KeyError, ValueError, InvalidVersion) as exc:
            raise FeedError(f"invalid advisory: {row!r}") from exc
        key = (adv.id, adv.purl_name)
        if key in seen:
            raise FeedError("duplicate advisory ID/package")
        seen.add(key)
        result.append(adv)
    return tuple(sorted(result, key=lambda a: (a.id, a.purl_name)))


def matches(component: Component, advisory: Advisory) -> bool:
    if purl_package(component.purl) != advisory.purl_name:
        return False
    try:
        v = Version(component.version)
        return v >= Version(advisory.introduced) and (advisory.fixed is None or v < Version(advisory.fixed))
    except InvalidVersion:
        return False
