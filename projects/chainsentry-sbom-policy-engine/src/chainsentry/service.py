"""Shared scan entry point for CLI and API."""
from __future__ import annotations
from datetime import date
from typing import Any
from .parser import parse_sbom
from .policy import evaluate
from .models import Report


def scan(sbom: dict[str, Any], advisories: dict[str, Any], policy: dict[str, Any], today: date | None = None) -> Report:
    return evaluate(parse_sbom(sbom), advisories, policy, today=today)
