from fastapi.testclient import TestClient

from aegis_feature_store.api import app


def test_api_lifecycle_and_auth(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_DB_PATH", str(tmp_path / "api.db"))
    monkeypatch.setenv("AEGIS_API_KEY", "test-key")
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").json()["registered_views"] == 0
        payload = {"name": "account_metrics", "version": 1,
                   "fields": {"balance": "number"}, "ttl_seconds": 3600}
        assert client.post("/v1/views", json=payload).status_code == 401
        headers = {"X-API-Key": "test-key"}
        assert client.post("/v1/views", json=payload, headers=headers).status_code == 201
        event = {"view_name": "account_metrics", "version": 1, "events": [{
            "event_id": "e1", "entity_key": "a1",
            "event_ts": "2026-01-01T12:00:00Z",
            "available_ts": "2026-01-01T12:00:00Z",
            "values": {"balance": 42.5},
        }]}
        assert client.post("/v1/events:ingest", json=event, headers=headers).json() == {
            "inserted": 1, "duplicates": 0,
        }
        joined = client.post("/v1/offline:join", headers=headers, json={
            "view_name": "account_metrics", "version": 1,
            "observations": [{"entity_key": "a1", "as_of": "2026-01-01T12:30:00Z"}],
        })
        assert joined.status_code == 200
        assert joined.json()["rows"][0]["features"]["balance"] == 42.5
        assert client.get("/metrics").status_code == 200
