import pytest
from quorumcraft import check_safety


def test_put_replicates(elected):
    assert elected.submit({"op": "put", "key": "x", "value": 17}, "put-1") == 1
    elected.tick(25)
    assert all(node.state.get("x") == 17 for node in elected.nodes.values())


def test_increment_is_deterministic(elected):
    elected.submit({"op": "put", "key": "x", "value": 10}, "p")
    elected.submit({"op": "increment", "key": "x", "value": -3}, "i")
    elected.tick(25)
    assert {node.state["x"] for node in elected.nodes.values()} == {7}


def test_delete(elected):
    elected.submit({"op": "put", "key": "x", "value": 1}, "p")
    elected.tick(15)
    elected.submit({"op": "delete", "key": "x"}, "d")
    elected.tick(15)
    assert all("x" not in node.state for node in elected.nodes.values())


def test_request_id_deduplication(elected):
    first = elected.submit({"op": "increment", "key": "count", "value": 1}, "same")
    second = elected.submit({"op": "increment", "key": "count", "value": 1}, "same")
    assert first == second
    elected.tick(25)
    assert {node.state["count"] for node in elected.nodes.values()} == {1}


def test_commit_requires_quorum(elected):
    leader = elected.leader()
    peers = [n for n in elected.nodes if n != leader.node_id]
    elected.partition([leader.node_id], peers)
    elected.submit({"op": "put", "key": "no", "value": 1}, "r")
    elected.tick(5)
    assert leader.commit_index == 0


def test_replicated_log_entries_match(elected):
    for i in range(4):
        elected.submit({"op": "put", "key": f"key-{i}", "value": i}, f"req-{i}")
    elected.tick(30)
    assert len({str([entry.to_dict() for entry in node.log]) for node in elected.nodes.values()}) == 1
    check_safety(elected.nodes)


@pytest.mark.parametrize("command", [{"op": "bad", "key": "x"}, {"op": "put", "key": ""},
                                     {"op": "increment", "key": "x", "value": "one"},
                                     {"op": "put", "key": "x"}])
def test_invalid_commands(elected, command):
    with pytest.raises(ValueError):
        elected.submit(command, "request")


def test_blank_request_id(elected):
    with pytest.raises(ValueError):
        elected.submit({"op": "delete", "key": "x"}, "")


def test_submit_without_leader():
    from quorumcraft import Cluster
    assert Cluster().submit({"op": "delete", "key": "x"}, "r") is None
