"""Command-line entrypoint for local database setup and registry inspection."""

import argparse
import json
import os

from atlasflow.db import Store
from atlasflow.service import RegistryService


def main() -> None:
    parser = argparse.ArgumentParser(description="AtlasFlow experiment registry")
    parser.add_argument("--db", default=os.environ.get("ATLAS_DB_PATH", "./var/atlasflow.sqlite3"))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init-db")
    show = commands.add_parser("show-run")
    show.add_argument("run_id")
    champion = commands.add_parser("champion")
    champion.add_argument("model_name")
    args = parser.parse_args()
    service = RegistryService(Store(args.db))
    if args.command == "init-db":
        print(f"Initialized {args.db}")
    elif args.command == "show-run":
        print(json.dumps(service.lineage(args.run_id), indent=2))
    elif args.command == "champion":
        print(json.dumps(service.get_champion(args.model_name), indent=2))


if __name__ == "__main__":
    main()
