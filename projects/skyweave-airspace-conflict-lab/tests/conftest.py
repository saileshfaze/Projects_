import pytest
from skyweave.scenarios import crossing,separated
from skyweave.models import flights_payload

@pytest.fixture
def crossing_flights():return crossing()
@pytest.fixture
def crossing_payload():return flights_payload(crossing())
@pytest.fixture
def separated_flights():return separated()
