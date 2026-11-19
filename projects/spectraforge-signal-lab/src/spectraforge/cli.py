"""Command line synthetic signal generation and spectral reporting."""
import argparse
import csv
import json
from pathlib import Path
from dataclasses import asdict
from .core import generate_signal, dominant_peaks, detect_anomalies

def main():
    parser = argparse.ArgumentParser(description="Synthetic DSP laboratory")
    parser.add_argument("--output", type=Path, default=Path("output/report.json"))
    parser.add_argument("--samples", type=int, default=256)
    parser.add_argument("--rate", type=float, default=256)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    samples = generate_signal(args.samples, args.rate, [(12, 1), (35, 0.4)], noise=0.05, seed=args.seed)
    peaks = dominant_peaks(samples, args.rate)
    report = {"sample_rate_hz": args.rate, "sample_count": len(samples), "seed": args.seed, "peaks": [asdict(p) for p in peaks], "anomaly_indices": detect_anomalies(samples)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="") as f:
            writer = csv.writer(f); writer.writerow(["index", "time_seconds", "amplitude"])
            for i, sample in enumerate(samples): writer.writerow([i, i / args.rate, sample])
    print(json.dumps(report, indent=2))
if __name__ == "__main__": main()
