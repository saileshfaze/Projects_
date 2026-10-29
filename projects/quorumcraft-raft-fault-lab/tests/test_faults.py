from quorumcraft import Cluster, check_safety


def test_crash_leader_and_recover(elected):
    former = elected.leader().node_id
    elected.crash(former)
    assert elected.leader() is None
    elected.tick(55)
    assert elected.leader() is not None
    assert elected.leader().node_id != former
    elected.recover(former)
    elected.tick(40)
    assert elected.nodes[former].active
    check_safety(elected.nodes)


def test_majority_partition_progress(elected):
    old_leader = elected.leader().node_id
    minority = [old_leader, next(n for n in elected.nodes if n != old_leader)]
    majority = [n for n in elected.nodes if n not in minority]
    elected.partition(minority, majority)
    elected.tick(65)
    assert elected.leader() is None or elected.leader().node_id in minority + majority
    # Partitioned minority cannot commit new entries even if it retains a leader role.
    minority_commit = max(elected.nodes[n].commit_index for n in minority)
    for node_id in minority:
        if elected.nodes[node_id].role == "leader":
            elected.submit({"op": "put", "key": "isolated", "value": 1}, "iso")
    elected.tick(8)
    assert max(elected.nodes[n].commit_index for n in minority) == minority_commit
    elected.heal()
    elected.tick(80)
    check_safety(elected.nodes)


def test_recovery_catches_up(elected):
    follower = next(n for n in elected.nodes if n != elected.leader().node_id)
    elected.crash(follower)
    elected.submit({"op": "put", "key": "x", "value": 7}, "r")
    elected.tick(25)
    assert elected.nodes[follower].last_index == 0
    elected.recover(follower)
    elected.tick(35)
    assert elected.nodes[follower].state["x"] == 7


def test_partition_blocks_bidirectional_links():
    c = Cluster()
    c.partition(["n1"], ["n2", "n3"])
    assert not c.network.allowed("n1", "n2")
    assert not c.network.allowed("n2", "n1")
    assert c.network.allowed("n4", "n5")
    c.heal()
    assert c.network.allowed("n1", "n2")


def test_unknown_partition_node_rejected():
    c = Cluster()
    try:
        c.partition(["n999"], ["n1"])
    except ValueError:
        pass
    else:
        raise AssertionError("expected validation error")


def test_crash_preserves_log(elected):
    leader = elected.leader().node_id
    elected.submit({"op": "put", "key": "a", "value": 1}, "r")
    elected.tick(15)
    before = list(elected.nodes[leader].log)
    elected.crash(leader)
    elected.recover(leader)
    assert elected.nodes[leader].log == before
