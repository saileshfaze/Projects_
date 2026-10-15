def example(event_id="evt-1"):
    return {
        "event_id": event_id,
        "event_type": "purchase",
        "occurred_at": "2026-10-01T10:00:00Z",
        "value": 12.5,
        "attributes": {"order_id": "order-1", "currency": "EUR"},
    }


def test_auth_required(client):
    assert client.post("/v1/tenants/demo/events", json={"events": [example()]}).status_code == 401


def test_batch_ingestion_and_query(client):
    headers = {"x-api-key": "test-key"}
    endpoint = "/v1/tenants/demo/events"
    first = client.post(endpoint, headers=headers, json={"events": [example()]})
    assert first.status_code == 200, first.text
    assert first.json()["accepted"] == 1
    second = client.post(endpoint, headers=headers, json={"events": [example()]})
    assert second.json()["duplicates"] == 1
    params = {
        "start": "2026-10-01T10:00:00Z",
        "end": "2026-10-01T12:00:00Z",
        "window_seconds": 3600,
    }
    windows = client.get("/v1/tenants/demo/windows", headers=headers, params=params)
    assert windows.status_code == 200
    assert windows.json()[0]["total_value"] == 12.5
    anomalies = client.get("/v1/tenants/demo/anomalies", headers=headers, params=params)
    assert anomalies.status_code == 200
    assert anomalies.json()[0]["anomalous"] is False


def test_contract_rejection_is_atomic(client):
    headers = {"x-api-key": "test-key"}
    bad = example("bad")
    bad["attributes"] = {}
    result = client.post(
        "/v1/tenants/demo/events",
        headers=headers,
        json={"events": [example("good"), bad]},
    )
    assert result.status_code == 422
    params = {"start": "2026-10-01T00:00:00Z", "end": "2026-10-02T00:00:00Z"}
    assert client.get("/v1/tenants/demo/windows", headers=headers, params=params).json() == []


def test_invalid_range(client):
    result = client.get(
        "/v1/tenants/demo/windows",
        headers={"x-api-key": "test-key"},
        params={"start": "2026-10-02T00:00:00Z", "end": "2026-10-01T00:00:00Z"},
    )
    assert result.status_code == 422


def test_health_and_metrics(client):
    assert client.get("/health").json()["status"] == "ok"
    assert "pulsemesh_ingest_events_total" in client.get("/metrics").text
