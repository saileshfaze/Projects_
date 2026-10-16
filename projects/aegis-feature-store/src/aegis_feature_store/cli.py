"""Command-line operations for local development and batch jobs."""

import argparse
import json
from pathlib import Path

from .config import Settings
from .models import FeatureEvent, FeatureView, Observation
from .store import FeatureStore


def main():
    parser = argparse.ArgumentParser(prog="aegis")
    parser.add_argument("--db", default=Settings.from_env().db_path)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize or migrate the SQLite database")
    sub.add_parser("stats", help="Print store statistics")
    register = sub.add_parser("register", help="Register view definition from JSON")
    register.add_argument("file")
    ingest = sub.add_parser("ingest", help="Ingest JSON event batch")
    ingest.add_argument("view")
    ingest.add_argument("version", type=int)
    ingest.add_argument("file")
    materialize = sub.add_parser("materialize", help="Build online snapshot")
    materialize.add_argument("view")
    materialize.add_argument("version", type=int)
    materialize.add_argument("as_of")
    join = sub.add_parser("join", help="Point-in-time join observations JSON")
    join.add_argument("view")
    join.add_argument("version", type=int)
    join.add_argument("file")
    args = parser.parse_args()
    store = FeatureStore(args.db)
    if args.command == "init":
        result = {"database": args.db, "initialized": True}
    elif args.command == "stats":
        result = store.stats()
    elif args.command == "register":
        result = store.register(FeatureView.model_validate_json(Path(args.file).read_text()))
    elif args.command == "ingest":
        events = json.loads(Path(args.file).read_text())
        result = store.ingest(args.view, args.version,
                              [FeatureEvent.model_validate(row) for row in events])
    elif args.command == "materialize":
        result = store.materialize(args.view, args.version, args.as_of)
    else:
        observations = json.loads(Path(args.file).read_text())
        result = store.offline_join(args.view, args.version,
                                    [Observation.model_validate(row) for row in observations])
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
