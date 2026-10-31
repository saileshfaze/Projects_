"""Command-line entrypoint."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .service import DEFAULT_SQL, analyze
from .synthetic import generate, save


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QueryWeaver cost-based SQL planner")
    parser.add_argument("--sql", default=DEFAULT_SQL, help="SQL text")
    parser.add_argument("--sql-file", type=Path, help="Read SQL from a UTF-8 file")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-cross", action="store_true")
    parser.add_argument("--format", choices=["json", "text", "dot"], default="text")
    parser.add_argument("--export-data", type=Path, help="Write synthetic CSV fixture files")
    args = parser.parse_args(argv)
    if args.export_data:
        counts = save(generate(seed=args.seed), args.export_data)
        print(json.dumps({"exported": counts}, sort_keys=True))
        return 0
    sql = args.sql_file.read_text(encoding="utf-8") if args.sql_file else args.sql
    result = analyze(sql, seed=args.seed, run=args.execute, allow_cross=args.allow_cross)
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.format == "dot":
        print(result["dot"])
    else:
        print(result["explain"])
        print(f"Baseline estimate: {result['baseline_cost']:.2f}; optimized: {result['optimized_cost']:.2f}")
        if args.execute:
            print(f"Actual result rows: {result['actual_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
