import pytest
from fastapi.testclient import TestClient
from chainsentry.api import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("CHAINSENTRY_DB", str(tmp_path / "api.db"))
    return TestClient(app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_scan_and_history(client, fixture_data):
    payload = {"project": "shop", "sbom": fixture_data("cyclonedx.json"),
               "advisories": fixture_data("advisories.json"), "policy": fixture_data("policy.json")}
    result = client.post("/v1/scans", json=payload)
    assert result.status_code == 200
    scan_id = result.json()["id"]
    assert client.get(f"/v1/scans/{scan_id}").json()["report"]["status"] == "fail"
    assert len(client.get("/v1/projects/shop/history").json()) == 1
    assert client.get(f"/v1/diff/{scan_id}/{scan_id}").json()["added"] == []


def test_invalid_document(client):
    r = client.post("/v1/scans", json={"project": "x", "sbom": {}, "advisories": {}, "policy": {}})
    assert r.status_code == 422


def test_missing_scan(client):
    assert client.get("/v1/scans/999").status_code == 404


def test_cross_project_diff_rejected(client, fixture_data):
    payload = {"project": "one", "sbom": fixture_data("cyclonedx.json"),
               "advisories": fixture_data("advisories.json"), "policy": fixture_data("policy.json")}
    a = client.post("/v1/scans", json=payload).json()["id"]
    payload["project"] = "two"
    b = client.post("/v1/scans", json=payload).json()["id"]
    assert client.get(f"/v1/diff/{a}/{b}").status_code == 422
