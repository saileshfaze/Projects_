"""Seed the small, fully synthetic demonstration dataset."""

import json
import os
from pathlib import Path

from aegis_feature_store.models import FeatureEvent, FeatureView
from aegis_feature_store.store import FeatureStore, StoreError

ROOT = Path(__file__).resolve().parents[1]
path = os.getenv("AEGIS_DB_PATH", str(ROOT / "data" / "aegis.db"))
store = FeatureStore(path)
view = FeatureView.model_validate_json((ROOT / "data/customer_risk_view.json").read_text())
try:
    store.register(view)
except StoreError as exc:
    if "already registered" not in str(exc):
        raise
events = json.loads((ROOT / "data/customer_risk_events.json").read_text())
result = store.ingest(view.name, view.version, [FeatureEvent.model_validate(e) for e in events])
result["materialization"] = store.materialize(
    view.name, view.version, "2026-01-02T12:00:00Z"
)
print(json.dumps(result, indent=2))
