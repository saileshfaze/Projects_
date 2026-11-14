"""CLI for local synthetic DNA analysis."""
import argparse
import json
from .analysis import analyze
from .fasta import read_fasta


def main(argv=None):
    parser = argparse.ArgumentParser(description="Synthetic DNA sequence analyzer")
    commands = parser.add_subparsers(dest="command", required=True)
    direct = commands.add_parser("analyze")
    direct.add_argument("--sequence", required=True)
    multi = commands.add_parser("fasta")
    multi.add_argument("path")
    multi.add_argument("--max-length", type=int, default=1_000_000)
    for cmd in (direct, multi):
        cmd.add_argument("--k", type=int, default=3)
        cmd.add_argument("--motif", default="ATG")
        cmd.add_argument("--min-codons", type=int, default=2)
    args = parser.parse_args(argv)
    if args.command == "analyze":
        result = analyze(args.sequence, args.k, args.motif, args.min_codons)
    else:
        result = {record.identifier: analyze(record.sequence, args.k, args.motif,
                                             args.min_codons)
                  for record in read_fasta(args.path, args.max_length)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
