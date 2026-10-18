from fastapi.testclient import TestClient
from routeforge.api import app

def test_health():
    assert TestClient(app).get("/health").json()["status"] == "ok"

def test_optimize_and_readback(raw_problem, tmp_path, monkeypatch):
    monkeypatch.setenv("ROUTEFORGE_DB", str(tmp_path / "test.db"))
    client = TestClient(app)
    response = client.post("/v1/optimize", json=raw_problem)
    assert response.status_code == 200, response.text
    plan = response.json()
    assert plan["jobs_total"] == 7
    read = client.get("/v1/plans/" + plan["plan_id"])
    assert read.status_code == 200
    assert read.json()["plan_id"] == plan["plan_id"]

def test_invalid_problem(raw_problem):
    raw_problem["jobs"][0]["demand"] = -1
    response = TestClient(app).post("/v1/optimize", json=raw_problem)
    assert response.status_code == 422
