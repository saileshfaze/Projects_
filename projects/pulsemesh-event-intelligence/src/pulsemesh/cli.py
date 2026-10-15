"""JSONL loader with deterministic, machine-readable ingestion summary."""
import argparse
from collections import Counter
import json
from pathlib import Path

from pydantic import ValidationError

from .contracts import validate_contract
from .models import Event
from .settings import Settings
from .storage import EventStore


def load(path: Path, tenant: str, store: EventStore) -> dict[str, int]:
    results: Counter[str] = Counter()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                event = Event.model_validate_json(line)
                validate_contract(event)
                results[store.ingest(tenant, event)] += 1
            except (ValidationError, ValueError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return dict(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="PulseMesh local event operations")
    sub = parser.add_subparsers(dest="command", required=True)
    loader = sub.add_parser("load", help="Import newline-delimited JSON events")
    loader.add_argument("path", type=Path)
    loader.add_argument("--tenant", default="demo")
    args = parser.parse_args()
    if args.command == "load":
        if not args.tenant or not args.tenant[0].islower() or not all(
            c.islower() or c.isdigit() or c in "_-" for c in args.tenant
        ) or len(args.tenant) > 64:
            parser.error("tenant must match lowercase slug pattern")
        config = Settings.from_env()
        store = EventStore(config.database_path, config.allowed_lateness_seconds)
        store.initialize()
        print(json.dumps(load(args.path, args.tenant, store), sort_keys=True))


if __name__ == "__main__":
    main()
