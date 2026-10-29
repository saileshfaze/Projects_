import json
import pytest
from quorumcraft import Cluster
from quorumcraft.scenarios import Action, demo_actions, run_scenario, actions_from_dict
from quorumcraft.synthetic import generate


def test_demo_converges():
    cluster = Cluster()
    run_scenario(cluster, demo_actions(), 150)
    assert all(node.state.get("orders") == 15 for node in cluster.nodes.values())
    assert cluster.audit.verify()


def test_scenario_seed_reproducible():
    a, b = Cluster(), Cluster()
    run_scenario(a, demo_actions(), 150)
    run_scenario(b, demo_actions(), 150)
    assert a.timeline == b.timeline
    assert a.audit.records == b.audit.records


def test_scenario_round_trip(tmp_path):
    path = generate(tmp_path / "scenario.json")
    data = json.loads(path.read_text())
    cluster = Cluster(size=data["nodes"], seed=data["seed"])
    run_scenario(cluster, actions_from_dict(data["actions"]), data["until"])
    assert cluster.now == 150


def test_unknown_action_raises():
    with pytest.raises(ValueError):
        run_scenario(Cluster(), [Action(0, "unknown", {})], 1)


def test_out_of_range_action_raises():
    with pytest.raises(ValueError):
        run_scenario(Cluster(), [Action(30, "heal", {})], 10)


def test_zero_ticks_allowed():
    c = Cluster()
    run_scenario(c, [], 0)
    assert c.now == 0
