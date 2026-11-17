import argparse
import json
from pathlib import Path
from .engine import canonical_report

def main():
    p = argparse.ArgumentParser(description='PolicyMesh deterministic authorization evaluator')
    p.add_argument('policy', type=Path)
    p.add_argument('requests', type=Path)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = canonical_report(json.loads(args.policy.read_text()), json.loads(args.requests.read_text()))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    else:
        print(result, end='')
if __name__ == '__main__': main()
