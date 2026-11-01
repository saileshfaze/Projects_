"""End-to-end offline demo with no persistent user data."""
from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from resonance.catalog import Catalog
from resonance.synthetic import make_clip


def main():
    with_catalog = Catalog()
    try:
        reference = make_clip(7, 3, "melody")
        other = make_clip(7, 3, "chirp")
        print("ingest", with_catalog.ingest("synthetic-melody", reference)["id"])
        print("ingest", with_catalog.ingest("synthetic-chirp", other)["id"])
        print("matches", with_catalog.search(reference))
    finally:
        with_catalog.close()

if __name__ == "__main__":
    main()
