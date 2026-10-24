import pytest
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from causalpilot.api import app


def test_api_smoke(tmp_path,monkeypatch):
    monkeypatch.setenv("CAUSALPILOT_DB",str(tmp_path/"api.db"))
    client=TestClient(app)
    assert client.get("/health").json()=={"status":"ok"}
    payload={"experiment_id":"api-exp","salt":"very-long-test-salt"}
    assert client.post("/experiments",json=payload).status_code==201
    assert client.get("/experiments/api-exp/assign/visitor-1").json()["arm"] in ("A","B")
    event={"event_id":"api-event-1","experiment_id":"api-exp","subject_id":"visitor-1", "revenue":10,"preperiod_revenue":2,"converted":True,"refunded":False,"timestamp":"2026-10-01T00:00:00Z"}
    assert client.post("/outcomes",json=event).json()=={"created":True}
    assert client.post("/outcomes",json=event).json()=={"created":False}
    assert client.get("/experiments/api-exp/report").json()["observed"]["A"]+client.get("/experiments/api-exp/report").json()["observed"]["B"]==1


def test_api_missing_experiment(tmp_path,monkeypatch):
    monkeypatch.setenv("CAUSALPILOT_DB",str(tmp_path/"missing.db"))
    assert TestClient(app).get("/experiments/nope/report").status_code==404
