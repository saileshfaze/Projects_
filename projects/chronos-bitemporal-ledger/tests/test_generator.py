import importlib.util
from pathlib import Path


def test_synthetic_generator_is_deterministic():
    path = Path(__file__).resolve().parents[1] / "scripts" / "generate_dataset.py"
    spec = importlib.util.spec_from_file_location("generator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    first = module.generate(seed=7, tenants=2, entities=3, revisions=2)
    second = module.generate(seed=7, tenants=2, entities=3, revisions=2)
    assert first == second
    assert len(first) == 12
    assert all(row["correction"]["valid_from"] < row["correction"]["valid_to"] for row in first)
