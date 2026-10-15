"""Validate per-event-type required attributes from bundled versioned contracts."""
import json
from functools import lru_cache
from importlib.resources import files

from .models import Event


@lru_cache(maxsize=1)
def load_contracts() -> dict:
    return json.loads(files("pulsemesh").joinpath("contracts.json").read_text())


def validate_contract(event: Event) -> None:
    definitions = load_contracts()
    versions = definitions.get(event.event_type)
    if versions is None:
        raise ValueError(f"Unknown event_type: {event.event_type}")
    definition = versions.get(str(event.schema_version))
    if definition is None:
        raise ValueError(f"Unsupported schema_version for {event.event_type}")
    for field, kind in definition["required"].items():
        value = event.attributes.get(field)
        if kind == "string" and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"{event.event_type}.{field} must be a non-empty string")
