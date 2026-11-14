"""Reproducible fictional FASTA fixture generator."""
import argparse
import random
from pathlib import Path

def generate(seed: int, records: int, length: int) -> str:
    if records < 1 or length < 9:
        raise ValueError("records >= 1 and length >= 9 required")
    rng = random.Random(seed)
    lines = []
    for i in range(records):
        sequence = "ATG" + "".join(rng.choices("ACGT", k=length-6)) + "TAA"
        lines.extend((f">fictional_{i:03d} seed={seed}", sequence))
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--records", type=int, default=10)
    parser.add_argument("--length", type=int, default=120)
    parser.add_argument("--output", default="output/synthetic.fasta")
    args = parser.parse_args()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(generate(args.seed, args.records, args.length), encoding="utf-8")
    print(f"Generated {args.records} fictional records: {target}")

if __name__ == "__main__":
    main()
