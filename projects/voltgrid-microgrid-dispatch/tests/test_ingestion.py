from pathlib import Path
import pytest
from voltgrid.ingestion import load_slots_csv

ROOT = Path(__file__).resolve().parents[1]

def test_csv_adapter():
    slots = load_slots_csv(ROOT / "data/demo_intervals.csv")
    assert len(slots) == 24
    assert slots[12].solar_kw == 8

def test_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("timestamp,load_kw\n2026-10-01T00:00:00Z,2\n")
    with pytest.raises(ValueError, match="missing CSV columns"):
        load_slots_csv(path)
