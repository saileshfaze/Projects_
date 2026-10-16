import pytest

from aegis_feature_store.models import FeatureEvent
from aegis_feature_store.store import StoreError


def event(**updates):
    data = {
        "event_id": "e1", "entity_key": "customer-1",
        "event_ts": "2026-01-02T12:00:00Z",
        "available_ts": "2026-01-02T12:01:00Z",
        "values": {"score": 0.7, "count": 3, "active": True},
    }
    data.update(updates)
    return FeatureEvent(**data)


def test_idempotent_ingestion(store):
    assert store.ingest("customer_risk", 1, [event()])["inserted"] == 1
    assert store.ingest("customer_risk", 1, [event()])["duplicates"] == 1
    assert store.stats()["ingested_events"] == 1


def test_conflicting_duplicate_rejected(store):
    store.ingest("customer_risk", 1, [event()])
    with pytest.raises(StoreError, match="Conflicting"):
        store.ingest("customer_risk", 1, [event(values={
            "score": 0.2, "count": 3, "active": True,
        })])


def test_batch_atomicity(store):
    with pytest.raises(StoreError):
        store.ingest("customer_risk", 1, [
            event(), event(event_id="e2", values={"score": "bad", "count": 3, "active": True}),
        ])
    assert store.stats()["ingested_events"] == 0


def test_reject_availability_before_event(store):
    with pytest.raises(StoreError, match="available_ts"):
        store.ingest("customer_risk", 1, [event(available_ts="2026-01-01T00:00:00Z")])


def test_timezone_required(store):
    with pytest.raises(ValueError, match="timezone"):
        store.ingest("customer_risk", 1, [event(event_ts="2026-01-02T12:00:00")])
