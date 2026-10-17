import hashlib
import json
from voltgrid.storage import RunStore, canonical_json

def test_persist_and_retrieve(tmp_path, scenario):
    store = RunStore(tmp_path / "nested" / "runs.sqlite3")
    payload = scenario.model_dump(mode="json")
    store.save("run-1", payload, {"status": "optimal"})
    stored = store.get("run-1")
    assert stored["result"]["status"] == "optimal"
    assert stored["scenario_sha256"] == hashlib.sha256(canonical_json(payload).encode()).hexdigest()
    assert store.get("missing") is None

def test_canonical_order():
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
