"""Strict CSV adapter for meter and tariff data."""

import csv
from pathlib import Path
from .domain import Slot

def load_slots_csv(path: str | Path) -> list[Slot]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = set(Slot.model_fields)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"missing CSV columns: {sorted(required - set(reader.fieldnames or []))}")
        slots = []
        for line, row in enumerate(reader, start=2):
            try:
                slots.append(Slot.model_validate(row))
            except Exception as exc:
                raise ValueError(f"invalid CSV row {line}: {exc}") from exc
        return slots
