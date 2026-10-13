"""CI-friendly offline contract gate: exit 1 on regression."""
import argparse
import json
from pathlib import Path

from .core import evaluate_samples


def main():
    parser = argparse.ArgumentParser(description="Evaluate response samples against a baseline")
    parser.add_argument("baseline", type=Path, help="JSON array of baseline response objects")
    parser.add_argument("candidate", type=Path, help="JSON array of candidate response objects")
    parser.add_argument("--lexical-limit", type=float, default=0.55)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    report = evaluate_samples(baseline, candidate, lexical_limit=args.lexical_limit)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
