import pytest
from quorumcraft import Cluster, SafetyViolation, check_safety
from quorumcraft.model import Entry


def test_fresh_cluster_safe():
    assert check_safety(Cluster().nodes)["committed_pairs_checked"] == 0


def test_bad_commit_index_detected():
    c = Cluster()
    c.nodes["n1"].commit_index = 2
    with pytest.raises(SafetyViolation):
        check_safety(c.nodes)


def test_duplicate_leaders_same_term_detected():
    c = Cluster()
    for node in (c.nodes["n1"], c.nodes["n2"]):
        node.role = "leader"
        node.current_term = 2
    with pytest.raises(SafetyViolation):
        check_safety(c.nodes)


def test_log_index_gap_detected():
    c = Cluster()
    c.nodes["n1"].log.append(Entry(1, 9, "bad", {"op": "delete", "key": "x"}))
    with pytest.raises(SafetyViolation):
        check_safety(c.nodes)


def test_state_divergence_detected():
    c = Cluster()
    c.nodes["n1"].state["x"] = 1
    with pytest.raises(SafetyViolation):
        check_safety(c.nodes)


def test_negative_tick_rejected():
    with pytest.raises(ValueError):
        Cluster().tick(-1)
