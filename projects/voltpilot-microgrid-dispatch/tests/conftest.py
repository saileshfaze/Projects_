import pytest
from voltpilot.synthetic import generate
from voltpilot.models import Site


@pytest.fixture
def profile():
    return generate(days=1, seed=42)


@pytest.fixture
def site():
    return Site()
