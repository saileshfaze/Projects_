import pytest
from quorumcraft.network import Network


def test_delivery_after_latency():
    network = Network(seed=3, latency=(2, 2))
    network.send(0, "a", "b", "ping", 1, {})
    assert network.receive(1, {"a", "b"}) == []
    assert len(network.receive(2, {"a", "b"})) == 1


def test_loss_one_drops_everything():
    network = Network(loss=1)
    for _ in range(10):
        network.send(0, "a", "b", "ping", 1, {})
    assert network.stats()["dropped"] == 10


def test_in_flight_partition_drops():
    network = Network(latency=(3, 3))
    network.send(0, "a", "b", "ping", 1, {})
    network.partition(["a"], ["b"])
    assert network.receive(3, {"a", "b"}) == []
    assert network.stats()["dropped"] == 1


def test_crashed_receiver_drops():
    network = Network(latency=(1, 1))
    network.send(0, "a", "b", "ping", 1, {})
    assert network.receive(1, {"a"}) == []
    assert network.stats()["dropped"] == 1


@pytest.mark.parametrize("latency,loss", [((0, 1), 0), ((4, 2), 0), ((1, 2), -0.1), ((1, 2), 1.1)])
def test_invalid_network_parameters(latency, loss):
    with pytest.raises(ValueError):
        Network(latency=latency, loss=loss)


def test_seed_reproducibility():
    a, b = Network(seed=15), Network(seed=15)
    for network in [a, b]:
        for _ in range(5):
            network.send(0, "a", "b", "ping", 1, {})
    assert [(p.due, p.sequence) for p in a.queue] == [(p.due, p.sequence) for p in b.queue]
