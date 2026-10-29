"""Generate deterministic scenario fixtures without external datasets."""
from __future__ import annotations
import json
from pathlib import Path
from .scenarios import demo_actions


def generate(path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    actions = [{"tick": action.tick, "kind": action.kind, "payload": action.payload}
               for action in demo_actions()]
    destination.write_text(json.dumps({"schema_version": 1, "name": "partition-and-heal",
                                       "seed": 42, "nodes": 5, "until": 150, "actions": actions},
                                      indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
