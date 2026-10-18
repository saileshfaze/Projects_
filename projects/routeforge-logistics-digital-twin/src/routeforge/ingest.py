"""Load validated problem JSON and persist deterministic reports."""
import json
from pathlib import Path
from .domain import Problem, parse_problem

def load_problem(path: str | Path) -> Problem:
    with Path(path).open(encoding="utf-8") as stream:
        return parse_problem(json.load(stream))

def dump_json(payload: dict, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
