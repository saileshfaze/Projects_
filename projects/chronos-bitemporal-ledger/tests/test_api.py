from fastapi.testclient import TestClient

from chronos_ledger import api


def test_api_write_read_and_audit(ledger, monkeypatch):
    monkeypatch.setattr(api, "get_ledger", lambda: ledger)
    client = TestClient(api.app)
    assert client.get("/healthz").json() == {"status": "ok"}
    body = {
        "valid_from": "2026-01-01", "valid_to": "2027-01-01",
        "payload": {"price": 49}, "actor": "demo", "idempotency_key": "api-1",
    }
    response = client.post("/v1/tenants/acme/entities/plan-1/corrections", json=body)
    assert response.status_code == 200, response.text
    response = client.get("/v1/tenants/acme/entities/plan-1?valid_at=2026-04-01")
    assert response.status_code == 200
    assert response.json()["payload"]["price"] == 49
    assert client.get("/v1/tenants/acme/audit").json()["valid"] is True


def test_api_validation_and_idempotency_conflict(ledger, monkeypatch):
    monkeypatch.setattr(api, "get_ledger", lambda: ledger)
    client = TestClient(api.app)
    endpoint = "/v1/tenants/acme/entities/e/corrections"
    body = {
        "valid_from": "2026-05-01", "valid_to": "2026-04-01",
        "payload": {}, "actor": "test", "idempotency_key": "key",
    }
    assert client.post(endpoint, json=body).status_code == 422
    body["valid_to"] = "2026-06-01"
    assert client.post(endpoint, json=body).status_code == 200
    body["payload"] = {"changed": True}
    assert client.post(endpoint, json=body).status_code == 409
    assert client.get("/v1/tenants/acme/entities/missing?valid_at=2026-05-01").status_code == 404
