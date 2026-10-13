from fastapi.testclient import TestClient

from app.api import app


def test_snapshot_evaluate_and_history(monkeypatch, tmp_path):
    monkeypatch.setenv("VECTORGUARD_DB", str(tmp_path / "store.db"))
    client = TestClient(app)
    created = client.post(
        "/v1/contracts/orders-v1/snapshots",
        json={"samples": [{"id": 1, "amount": 10}, {"id": 2, "amount": 11}]},
    )
    assert created.status_code == 201
    assert created.json()["version"] == 1
    result = client.post(
        "/v1/contracts/orders-v1/evaluate",
        json={"samples": [{"id": 3, "amount": "invalid"}]},
    )
    assert result.status_code == 201
    assert result.json()["breaking"]
    assert result.json()["verdict"] == "fail"
    evaluation_id = result.json()["evaluation_id"]
    assert client.get(f"/v1/evaluations/{evaluation_id}").json()["report"]["breaking"]
    assert len(client.get("/v1/contracts/orders-v1/snapshots").json()["snapshots"]) == 1


def test_auth_and_validation(monkeypatch, tmp_path):
    monkeypatch.setenv("VECTORGUARD_DB", str(tmp_path / "store.db"))
    monkeypatch.setenv("VECTORGUARD_API_KEY", "test-secret")
    client = TestClient(app)
    path = "/v1/contracts/orders-v1/snapshots"
    assert client.post(path, json={"samples": [{"id": 1}]}).status_code == 401
    assert client.post(
        path, headers={"x-api-key": "test-secret"}, json={"samples": [{"id": 1}]}
    ).status_code == 201
    assert client.post(
        "/v1/contracts/BAD/snapshots",
        headers={"x-api-key": "test-secret"},
        json={"samples": [{"id": 1}]},
    ).status_code == 422


def test_metric_drift(monkeypatch, tmp_path):
    monkeypatch.setenv("VECTORGUARD_DB", str(tmp_path / "store.db"))
    client = TestClient(app)
    client.post(
        "/v1/contracts/prices/snapshots",
        json={"samples": [{"price": x} for x in range(20)]},
    )
    result = client.post(
        "/v1/contracts/prices/evaluate",
        json={"samples": [{"price": x + 100} for x in range(20)], "metric_path": "price"},
    )
    assert result.status_code == 201
    assert result.json()["metric_drift"]["drift_detected"]
