import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture
def fixture_data():
    return lambda name: json.loads((ROOT / name).read_text(encoding="utf-8"))
