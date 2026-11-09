import json
from pathlib import Path
import pytest
from hydrograph.model import from_dict
@pytest.fixture
def network():return from_dict(json.loads((Path(__file__).parents[1]/'data/network.json').read_text()))
