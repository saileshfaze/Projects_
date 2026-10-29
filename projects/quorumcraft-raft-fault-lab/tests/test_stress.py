import pytest
from quorumcraft import Cluster, check_safety


@pytest.mark.parametrize("seed", [0, 4, 17, 28, 63, 101, 999])
def test_lossy_network_preserves_safety(seed):
    cluster = Cluster(seed=seed, loss=0.12)
    cluster.tick(220)
    check_safety(cluster.nodes)
    assert cluster.audit.verify()


@pytest.mark.parametrize("seed", [7, 19, 37])
def test_partition_recovery_preserves_safety(seed):
    cluster = Cluster(seed=seed)
    cluster.tick(35)
    cluster.partition(["n1", "n2"], ["n3", "n4", "n5"])
    cluster.tick(90)
    cluster.heal()
    cluster.tick(110)
    check_safety(cluster.nodes)
