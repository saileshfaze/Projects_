import pytest
from quorumcraft import Cluster


@pytest.fixture
def elected():
    cluster = Cluster(seed=42)
    cluster.tick(35)
    assert cluster.leader() is not None
    return cluster
