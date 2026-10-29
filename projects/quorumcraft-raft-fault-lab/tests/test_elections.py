import pytest
from quorumcraft import Cluster, check_safety


@pytest.mark.parametrize("size", [3, 5, 7])
def test_cluster_elects_one_leader(size):
    cluster = Cluster(size=size, seed=42)
    cluster.tick(60)
    assert cluster.leader() is not None
    assert sum(node.role == "leader" for node in cluster.nodes.values()) == 1
    assert check_safety(cluster.nodes)["active_leaders"] == 1


@pytest.mark.parametrize("seed", [1, 2, 3, 42, 99])
def test_elections_across_seeds(seed):
    cluster = Cluster(seed=seed)
    cluster.tick(100)
    assert cluster.leader()


def test_candidate_votes_for_self():
    cluster = Cluster(seed=42)
    cluster.tick(10)
    candidates = [n for n in cluster.nodes.values() if n.role == "candidate"]
    assert all(n.voted_for == n.node_id for n in candidates)


def test_odd_cluster_required():
    for size in [0, 1, 2, 4, 6]:
        with pytest.raises(ValueError):
            Cluster(size=size)


def test_election_timeout_validation():
    with pytest.raises(ValueError):
        Cluster(election_range=(3, 7), heartbeat=2)


def test_leader_term_positive(elected):
    assert elected.leader().current_term >= 1


def test_no_leader_initially():
    assert Cluster().leader() is None
