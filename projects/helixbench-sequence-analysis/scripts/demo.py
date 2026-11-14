"""End-to-end synthetic sequence demonstration."""
import json
from pathlib import Path
from helixbench.analysis import analyze
from helixbench.fasta import read_fasta

def main():
    root = Path(__file__).resolve().parents[1]
    records = read_fasta(root / "data/synthetic.fasta")
    reports = {item.identifier: analyze(item.sequence) for item in records}
    assert len(reports) == 2
    assert reports["synthetic_alpha"]["orfs"]
    print(json.dumps(reports, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
