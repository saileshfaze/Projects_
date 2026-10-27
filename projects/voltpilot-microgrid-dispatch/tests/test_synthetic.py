from voltpilot.synthetic import generate,save_json,load_json,save_csv
import pytest


def test_deterministic_generation():
    assert generate(seed=11)==generate(seed=11)
    assert generate(seed=11)!=generate(seed=12)


def test_profile_roundtrip(tmp_path):
    p=generate(days=1)
    f=tmp_path/"data.json"
    save_json(p,f)
    assert load_json(f)==p


def test_csv_output(tmp_path):
    f=tmp_path/"data.csv"
    save_csv(generate(days=1),f)
    assert len(f.read_text().splitlines())==97


def test_invalid_days():
    with pytest.raises(ValueError): generate(days=0)


def test_outage_generation():
    p=generate(days=1,outage_start=10,outage_length=3)
    assert sum(not x.grid_available for x in p)==3
