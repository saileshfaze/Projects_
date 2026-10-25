"""CLI entry point for reproducible generation, analysis and evaluation."""
import argparse
import json
from pathlib import Path
import numpy as np
from .evaluation import evaluate
from .io import load_pair, safe_dataset, write_report
from .models import Settings
from .pipeline import analyze
from .synthetic import generate
from .visuals import quicklook, mask_preview


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="terraflux")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="generate synthetic scene pair")
    gen.add_argument("--root", type=Path, default=Path("data/generated"))
    gen.add_argument("--id", default="demo")
    gen.add_argument("--size", type=int, default=96)
    gen.add_argument("--seed", type=int, default=7)
    run = sub.add_parser("analyze", help="analyze an existing dataset")
    run.add_argument("dataset_id")
    run.add_argument("--root", type=Path, default=Path("data/generated"))
    run.add_argument("--output", type=Path, default=Path("out/report.json"))
    ev = sub.add_parser("evaluate", help="compare detection against synthetic truth")
    ev.add_argument("dataset_id")
    ev.add_argument("--root", type=Path, default=Path("data/generated"))
    img = sub.add_parser("quicklook", help="render false-color scene previews")
    img.add_argument("dataset_id")
    img.add_argument("--root", type=Path, default=Path("data/generated"))
    img.add_argument("--out", type=Path, default=Path("out/images"))
    args = parser.parse_args(argv)
    if args.command == "generate":
        print(generate(args.root, args.id, args.size, args.seed))
    else:
        before, after = load_pair(args.root, args.dataset_id)
        if args.command == "analyze":
            result = analyze(before, after, Settings())
            write_report(args.output, result)
            print(json.dumps(result["summary"], indent=2))
        elif args.command == "evaluate":
            truth = np.load(safe_dataset(args.root, args.dataset_id) / "truth.npy", allow_pickle=False)
            print(json.dumps(evaluate(before, after, truth), indent=2))
        else:
            quicklook(before, args.out / "before.png")
            quicklook(after, args.out / "after.png")
            mask_preview(before.cloud | after.cloud, args.out / "cloud-mask.png")
            print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
