import pytest
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from voltpilot.api import app
from voltpilot.synthetic import generate
from dataclasses import asdict


def test_health():
    assert TestClient(app).get("/health").json()["status"]=="ok"


def test_simulation_and_lookup(tmp_path,monkeypatch):
    monkeypatch.setenv("VOLTPILOT_DB",str(tmp_path/"api.db"))
    client=TestClient(app)
    body={"intervals":[asdict(x) for x in generate(days=1)]}
    r=client.post("/simulate",json=body)
    assert r.status_code==200, r.text
    rid=r.json()["id"]
    assert client.get(f"/runs/{rid}").json()["audit_valid"]
    assert len(client.get("/runs").json())==1
    assert len(client.post("/compare",json=body).json())==4


def test_invalid_input_is_422():
    client=TestClient(app)
    assert client.post("/simulate",json={"intervals":[]}).status_code==422
    assert client.get("/runs/unknown").status_code==404
