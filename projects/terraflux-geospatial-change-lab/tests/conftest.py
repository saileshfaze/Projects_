import pytest
from terraflux.synthetic import make_pair


@pytest.fixture
def pair():
    return make_pair(size=48, seed=7)
