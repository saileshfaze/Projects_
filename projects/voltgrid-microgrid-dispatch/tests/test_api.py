from fastapi.testclient import TestClient
from voltgrid.api import app, get_store
from voltgrid.storage import RunStore

def test_dispatch_roundtrip(tmp_path, scenario):
    app.dependency_overrides[get_store] = lambda: RunStore(tmp_path / "api.sqlite3")
    try:
        with TestClient(app) as client:
            response = client.post("/v1/dispatches", json=scenario.model_dump(mode="json"))
            assert response.status_code == 201, response.text
            run_id = response.json()["run_id"]
            found = client.get(f"/v1/dispatches/{run_id}")
            assert found.status_code == 200
            assert found.json()["result"]["status"] == "optimal"
            assert client.get("/v1/dispatches/missing").status_code == 404
            assert client.get("/healthz").json()["status"] == "ok"
    finally:
        app.dependency_overrides.clear()

def test_forecast_endpoint():
    with TestClient(app) as client:
        response = client.post("/v1/forecast",
            json={"history_kw": [1, 2, 1, 2], "horizon": 2, "season_length": 2})
        assert response.status_code == 200
        assert response.json()["point"] == [1, 2]
