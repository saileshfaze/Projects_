import json
from pathlib import Path
import pytest
from routeforge.domain import parse_problem

@pytest.fixture
def raw_problem():
    path = Path(__file__).resolve().parents[1] / "data" / "example_problem.json"
    return json.loads(path.read_text(encoding="utf-8"))

@pytest.fixture
def problem(raw_problem):
    return parse_problem(raw_problem)
