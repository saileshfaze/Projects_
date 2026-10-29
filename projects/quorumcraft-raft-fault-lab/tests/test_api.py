from fastapi.testclient import TestClient
from quorumcraft.api import create_app
from quorumcraft import Cluster


def test_health():
    client = TestClient(create_app(Cluster()))
    assert client.get("/health").json()["status"] == "ok"


def test_tick_and_cluster():
    client = TestClient(create_app(Cluster()))
    assert client.post("/tick", json={"steps": 35}).status_code == 200
    assert client.get("/cluster").json()["leader"] is not None


def test_command_before_election_returns_503():
    client = TestClient(create_app(Cluster()))
    r = client.post("/commands", json={"request_id": "r", "op": "put", "key": "x", "value": 1})
    assert r.status_code == 503


def test_command_accept_and_commit():
    client = TestClient(create_app(Cluster()))
    client.post("/tick", json={"steps": 35})
    assert client.post("/commands", json={"request_id": "r", "op": "put", "key": "x", "value": 1}).status_code == 200
    client.post("/tick", json={"steps": 25})
    assert all(n["state"].get("x") == 1 for n in client.get("/cluster").json()["nodes"])


def test_fault_endpoint():
    client = TestClient(create_app(Cluster()))
    assert client.post("/faults", json={"kind": "partition", "a": ["n1"], "b": ["n2"]}).status_code == 200
    assert client.post("/faults", json={"kind": "heal"}).status_code == 200
    assert client.post("/faults", json={"kind": "crash", "node": "missing"}).status_code == 422


def test_metrics_and_audit():
    client = TestClient(create_app(Cluster()))
    client.post("/tick", json={"steps": 15})
    assert client.get("/metrics").json()["ticks"] == 15
    assert client.get("/audit").json()["valid"] is True


def test_invalid_tick_request():
    client = TestClient(create_app(Cluster()))
    assert client.post("/tick", json={"steps": 0}).status_code == 422
