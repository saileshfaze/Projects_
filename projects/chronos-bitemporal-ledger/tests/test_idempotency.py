import pytest

from chronos_ledger.models import Correction
from chronos_ledger.service import IdempotencyConflict


def event(status, key="same"):
    return Correction(
        valid_from="2026-01-01", valid_to="2027-01-01",
        payload={"status": status}, actor="alice", idempotency_key=key,
    )


def test_retry_returns_same_operation_without_new_history(ledger):
    first = ledger.correct("t", "e", event("open"))
    second = ledger.correct("t", "e", event("open"))
    assert second.replayed is True
    assert first.operation_id == second.operation_id
    assert len(ledger.history("t", "e")) == 1


def test_reusing_key_with_different_body_fails(ledger):
    ledger.correct("t", "e", event("open"))
    with pytest.raises(IdempotencyConflict):
        ledger.correct("t", "e", event("closed"))


def test_same_key_allowed_for_different_tenant(ledger):
    ledger.correct("t1", "e", event("open"))
    ledger.correct("t2", "e", event("closed"))
    assert len(ledger.history("t2", "e")) == 1
