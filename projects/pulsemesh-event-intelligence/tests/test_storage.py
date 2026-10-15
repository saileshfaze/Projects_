from datetime import datetime, timedelta, timezone

from pulsemesh.models import Event


def make_event(event_id, minute=0):
    return Event(
        event_id=event_id,
        event_type="click",
        occurred_at=datetime(2026, 10, 1, tzinfo=timezone.utc) + timedelta(minutes=minute),
        attributes={"page": "/", "session_id": "s"},
    )


def test_deduplication_and_tenant_isolation(store):
    assert store.ingest("alpha", make_event("one")) == "accepted"
    assert store.ingest("alpha", make_event("one")) == "duplicate"
    assert store.ingest("beta", make_event("one")) == "accepted"
    assert store.count("alpha") == 1
    assert store.count("beta") == 1


def test_watermark_late_event_rejected(store):
    assert store.ingest("alpha", make_event("latest", 120)) == "accepted"
    assert store.ingest("alpha", make_event("late", 1)) == "late"
    assert store.ingest("alpha", make_event("within", 90)) == "accepted"
    assert store.count("alpha") == 2


def test_half_open_window_and_value_sum(store):
    store.ingest("alpha", make_event("one", 0))
    store.ingest("alpha", make_event("two", 60))
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    assert store.windows("alpha", start, start + timedelta(hours=1), 3600)[0]["count"] == 1
    assert store.windows("alpha", start, start + timedelta(hours=2), 3600)[1]["count"] == 1
    assert store.windows("beta", start, start + timedelta(hours=2), 3600) == []
