"""End-to-end local demo with synthetic truth and evidence exports."""
from pathlib import Path
import json
import numpy as np
from terraflux.synthetic import generate
from terraflux.io import load_pair, write_report
from terraflux.pipeline import analyze
from terraflux.evaluation import evaluate
from terraflux.visuals import quicklook


def main() -> None:
    root = Path("data/generated")
    dataset = "demo"
    if not (root / dataset).exists():
        generate(root, dataset)
    before, after = load_pair(root, dataset)
    report = analyze(before, after)
    out = Path("out")
    write_report(out / "report.json", report)
    write_report(out / "changes.geojson", report["geojson"])
    quicklook(before, out / "before.png")
    quicklook(after, out / "after.png")
    truth = np.load(root / dataset / "truth.npy", allow_pickle=False)
    metrics = evaluate(before, after, truth)
    write_report(out / "evaluation.json", metrics)
    print(json.dumps({"summary": report["summary"], "evaluation": metrics}, indent=2))


if __name__ == "__main__":
    main()
