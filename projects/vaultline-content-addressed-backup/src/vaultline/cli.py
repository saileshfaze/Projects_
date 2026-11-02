"""Command-line interface. Exit code 2 indicates a handled Vaultline error."""
import argparse
import json
import sys
from pathlib import Path
from .engine import Vault
from .errors import VaultlineError
from .report import svg_report

def main(argv=None):
    parser = argparse.ArgumentParser(prog="vaultline")
    parser.add_argument("--vault", default=".vaultline", help="vault storage directory")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("snapshot"); p.add_argument("source"); p.add_argument("--label", default="")
    p = sub.add_parser("restore"); p.add_argument("id"); p.add_argument("target"); p.add_argument("--overwrite", action="store_true")
    p = sub.add_parser("verify"); p.add_argument("id")
    sub.add_parser("list")
    sub.add_parser("stats")
    p = sub.add_parser("prune"); p.add_argument("--keep", type=int, default=3); p.add_argument("--apply", action="store_true")
    p = sub.add_parser("report"); p.add_argument("output")
    sub.add_parser("audit")
    args = parser.parse_args(argv)
    try:
        vault = Vault(args.vault)
        if args.command == "snapshot": result = vault.snapshot(args.source, args.label)
        elif args.command == "restore": result = vault.restore(args.id, args.target, args.overwrite)
        elif args.command == "verify": result = vault.verify(args.id)
        elif args.command == "list": result = vault.list_snapshots()
        elif args.command == "stats": result = vault.stats()
        elif args.command == "prune": result = vault.prune(args.keep, not args.apply)
        elif args.command == "audit": result = {"events": vault.audit.verify(), "ok": True}
        else:
            Path(args.output).write_text(svg_report(vault), encoding="utf-8")
            result = {"report": args.output}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (VaultlineError, ValueError, OSError) as exc:
        print(f"vaultline: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
