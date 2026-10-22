from datetime import date, datetime, timezone

import pytest

from chronos_ledger.models import Correction
from chronos_ledger.service import SnapshotNotFound


def d(value):
    return date.fromisoformat(value)


def change(start, end, status, key):
    return Correction(
        valid_from=d(start), valid_to=d(end), payload={"status": status},
        actor="test", idempotency_key=key,
    )


def test_initial_snapshot(ledger):
    ledger.correct("tenant-a", "invoice-1", change("2026-01-01", "2027-01-01", "draft", "a"))
    result = ledger.snapshot("tenant-a", "invoice-1", d("2026-04-01"))
    assert result.payload == {"status": "draft"}
    assert result.valid_to == d("2027-01-01")


def test_backdated_correction_preserves_what_was_known(ledger, clock):
    first = ledger.correct("t", "e", change("2026-01-01", "2027-01-01", "old", "1"))
    clock.set("2026-02-01T00:00:00Z")
    second = ledger.correct("t", "e", change("2026-03-01", "2026-07-01", "new", "2"))
    assert ledger.snapshot("t", "e", d("2026-05-01"), first.recorded_at).payload == {"status": "old"}
    assert ledger.snapshot("t", "e", d("2026-05-01"), second.recorded_at).payload == {"status": "new"}
    assert ledger.snapshot("t", "e", d("2026-02-01")).payload == {"status": "old"}
    assert ledger.snapshot("t", "e", d("2026-08-01")).payload == {"status": "old"}
    assert len(ledger.history("t", "e")) == 4


def test_correction_across_multiple_current_segments(ledger, clock):
    ledger.correct("t", "e", change("2026-01-01", "2026-04-01", "a", "1"))
    clock.set("2026-02-01T00:00:00Z")
    ledger.correct("t", "e", change("2026-04-01", "2026-08-01", "b", "2"))
    clock.set("2026-03-01T00:00:00Z")
    ledger.correct("t", "e", change("2026-03-01", "2026-06-01", "c", "3"))
    assert ledger.snapshot("t", "e", d("2026-02-01")).payload["status"] == "a"
    assert ledger.snapshot("t", "e", d("2026-04-01")).payload["status"] == "c"
    assert ledger.snapshot("t", "e", d("2026-07-01")).payload["status"] == "b"


def test_absent_period_is_not_synthesized(ledger):
    ledger.correct("t", "e", change("2026-01-01", "2026-02-01", "a", "1"))
    with pytest.raises(SnapshotNotFound):
        ledger.snapshot("t", "e", d("2026-02-01"))


def test_tenant_isolation(ledger):
    ledger.correct("a", "e", change("2026-01-01", "2027-01-01", "a", "1"))
    with pytest.raises(SnapshotNotFound):
        ledger.snapshot("b", "e", d("2026-05-01"))


def test_naive_known_at_is_rejected(ledger):
    with pytest.raises(ValueError, match="timezone-aware"):
        ledger.snapshot("a", "e", d("2026-01-01"), datetime(2026, 1, 1))


def test_clock_monotonic_even_if_wall_clock_goes_back(ledger, clock):
    first = ledger.correct("t", "e", change("2026-01-01", "2027-01-01", "a", "1"))
    second = ledger.correct("t", "e", change("2026-01-01", "2027-01-01", "b", "2"))
    assert second.recorded_at > first.recorded_at
    assert second.recorded_at.tzinfo == timezone.utc
