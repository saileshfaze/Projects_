"""CLI for generation, catalog operations and offline analysis."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .catalog import Catalog
from .synthetic import make_clip
from .waveio import read_wav
from .dsp import extract_features
from .report import spectrogram_svg
from .batch import ingest_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="resonance")
    parser.add_argument("--db", default="resonance.sqlite")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("output")
    gen.add_argument("--seed", type=int, default=7)
    gen.add_argument("--variant", choices=["melody", "chirp", "noise", "silence"], default="melody")
    analyze = sub.add_parser("analyze")
    analyze.add_argument("wav")
    analyze.add_argument("--svg")
    ingest = sub.add_parser("ingest")
    ingest.add_argument("wav")
    scan = sub.add_parser("scan")
    scan.add_argument("directory")
    search = sub.add_parser("search")
    search.add_argument("wav")
    sub.add_parser("list")
    args = parser.parse_args(argv)
    if args.command == "generate":
        Path(args.output).write_bytes(make_clip(seed=args.seed, variant=args.variant))
        print(json.dumps({"written": args.output}))
    elif args.command == "analyze":
        audio = read_wav(args.wav)
        if args.svg:
            Path(args.svg).write_text(spectrogram_svg(audio), encoding="utf-8")
        print(json.dumps(extract_features(audio).to_dict(), sort_keys=True))
    else:
        db = Catalog(args.db)
        try:
            if args.command == "ingest":
                result = db.ingest(Path(args.wav).name, Path(args.wav).read_bytes())
            elif args.command == "scan":
                result = ingest_directory(db, args.directory)
            elif args.command == "search":
                result = db.search(Path(args.wav).read_bytes())
            else:
                result = db.list_clips()
            print(json.dumps(result, sort_keys=True))
        finally:
            db.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
