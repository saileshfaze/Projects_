import json

from pulsemesh.cli import load


def test_load_jsonl(tmp_path, store):
    path = tmp_path / "events.jsonl"
    event = {
        "event_id": "sample-1",
        "event_type": "telemetry",
        "occurred_at": "2026-10-01T00:00:00Z",
        "attributes": {"device_id": "sensor-1"},
    }
    path.write_text(json.dumps(event) + "\n" + json.dumps(event) + "\n")
    assert load(path, "demo", store) == {"accepted": 1, "duplicate": 1}
