from aegis_feature_store.models import FeatureEvent, Observation


def add(store, event_id, event_ts, available_ts, score, entity="c1"):
    store.ingest("customer_risk", 1, [FeatureEvent(
        event_id=event_id, entity_key=entity, event_ts=event_ts,
        available_ts=available_ts,
        values={"score": score, "count": 1, "active": True},
    )])


def test_prevents_future_and_late_arrival_leakage(store):
    add(store, "old", "2026-01-01T09:00:00Z", "2026-01-01T09:00:00Z", 0.1)
    add(store, "late", "2026-01-01T10:00:00Z", "2026-01-01T15:00:00Z", 0.9)
    add(store, "future", "2026-01-02T09:00:00Z", "2026-01-02T09:00:00Z", 0.8)
    rows = store.offline_join("customer_risk", 1, [
        Observation(entity_key="c1", as_of="2026-01-01T12:00:00Z"),
        Observation(entity_key="c1", as_of="2026-01-01T16:00:00Z"),
        Observation(entity_key="c1", as_of="2026-01-02T10:00:00Z"),
    ])
    assert [row["event_id"] for row in rows] == ["old", "late", "future"]


def test_ttl_expires_old_values(store):
    add(store, "old", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", 0.5)
    row = store.offline_join("customer_risk", 1, [
        Observation(entity_key="c1", as_of="2026-01-03T00:00:00Z"),
    ])[0]
    assert row["features"] is None


def test_materialization_and_online_read(store):
    add(store, "old", "2026-01-01T09:00:00Z", "2026-01-01T09:00:00Z", 0.1)
    add(store, "new", "2026-01-01T10:00:00Z", "2026-01-01T10:00:00Z", 0.7)
    result = store.materialize("customer_risk", 1, "2026-01-01T12:00:00Z")
    assert result["materialized_entities"] == 1
    assert store.online_get("customer_risk", 1, "c1",
                            "2026-01-01T12:01:00Z")["event_id"] == "new"
    assert store.online_get("customer_risk", 1, "c1",
                            "2026-01-03T12:00:00Z") is None


def test_materialization_removes_stale_rows(store):
    add(store, "old", "2026-01-01T09:00:00Z", "2026-01-01T09:00:00Z", 0.1)
    store.materialize("customer_risk", 1, "2026-01-01T12:00:00Z")
    store.materialize("customer_risk", 1, "2026-01-03T12:00:00Z")
    assert store.stats()["online_entities"] == 0
