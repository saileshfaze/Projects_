from fastapi.testclient import TestClient

from atlasflow.api import create_app


def test_health_and_openapi(tmp_path):
    with TestClient(create_app(str(tmp_path / "api.db"))) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert "/v1/runs" in client.get("/openapi.json").json()["paths"]


def test_full_api_workflow(tmp_path):
    with TestClient(create_app(str(tmp_path / "api.db"))) as client:
        dataset = client.post("/v1/datasets", json={
            "name": "synthetic", "sha256": "a" * 64, "row_count": 20
        })
        assert dataset.status_code == 201
        run = client.post("/v1/runs", json={
            "dataset_id": dataset.json()["id"], "model_name": "model-one",
            "algorithm": "logistic", "seed": 12, "idempotency_key": "request-12345678"
        })
        assert run.status_code == 201
        run_id = run.json()["id"]
        assert client.post(f"/v1/runs/{run_id}/evaluate", json={
            "accuracy": 0.91, "precision": 0.9, "recall": 0.9,
            "f1": 0.9, "drift_psi": 0.1
        }).status_code == 200
        promotion = client.post(f"/v1/runs/{run_id}/promote", json={})
        assert promotion.json()["accepted"]
        assert client.get("/v1/models/model-one/champion").json()["id"] == run_id
        assert client.get(f"/v1/runs/{run_id}/lineage").json()["dataset"]["row_count"] == 20
        assert len(client.get(f"/v1/runs/{run_id}/audit").json()) == 1


def test_invalid_input_and_missing_run(tmp_path):
    with TestClient(create_app(str(tmp_path / "api.db"))) as client:
        assert client.post("/v1/datasets", json={
            "name": "bad", "sha256": "short", "row_count": -1
        }).status_code == 422
        assert client.get("/v1/runs/not-found").status_code == 404
