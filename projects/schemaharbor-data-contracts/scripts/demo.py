"""Reproducible end-to-end CLI demonstration."""
from pathlib import Path
from schemaharbor.cli import main

if __name__ == "__main__":
    base=Path(__file__).resolve().parents[1]
    main(["diff",str(base/"data/orders-v1.json"),str(base/"data/orders-v2.json")])
    main(["impact",str(base/"data/lineage.json"),"orders"])
