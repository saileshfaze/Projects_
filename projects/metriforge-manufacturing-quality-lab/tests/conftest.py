import pytest
from metriforge.synthetic import generate
from metriforge.models import QualitySpec
@pytest.fixture
def scenario(): return generate()
@pytest.fixture
def spec(): return QualitySpec('diameter_mm',48,52,50,'mm')
