import pytest

from atlasflow.synthetic import make_rows, write_csv


def test_synthetic_generation_deterministic(tmp_path):
    a = make_rows(30, 10)
    b = make_rows(30, 10)
    assert a == b
    assert len(a) == 30
    write_csv(tmp_path / "data.csv", a)
    assert (tmp_path / "data.csv").read_text().count("\n") == 31


def test_sklearn_training_optional():
    pytest.importorskip("sklearn")
    from atlasflow.training import train_and_evaluate

    result = train_and_evaluate(make_rows(320, 2026), seed=42)
    assert result["train_rows"] == 240
    assert result["test_rows"] == 80
    assert 0 <= result["metrics"]["f1"] <= 1
    assert result["drift_psi"] >= 0
