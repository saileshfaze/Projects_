from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from pulsemesh.contracts import validate_contract
from pulsemesh.models import Event


def event(**changes):
    payload = {
        "event_id": "evt-1",
        "event_type": "click",
        "occurred_at": "2026-10-01T10:00:00Z",
        "attributes": {"page": "/", "session_id": "s-1"},
    }
    payload.update(changes)
    return Event.model_validate(payload)


def test_contract_passes():
    validate_contract(event())


def test_contract_requires_attributes():
    with pytest.raises(ValueError, match="session_id"):
        validate_contract(event(attributes={"page": "/"}))


def test_unknown_version_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        validate_contract(event(schema_version=2))


def test_naive_time_rejected():
    with pytest.raises(ValidationError):
        event(occurred_at=datetime(2026, 10, 1, 10, 0))


def test_time_normalized():
    assert event().occurred_at.tzinfo == timezone.utc
