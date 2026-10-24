import pytest
from causalpilot.models import Experiment, Outcome
from causalpilot.service import ExperimentService


def event(id="evt-1", user="visitor-1", revenue=10.0):
    return Outcome(id,"checkout-v2",user,revenue,3.0,True,False,"2026-10-01T12:00:00Z")


def test_register_is_idempotent(service,config):
    service.register(config)


def test_register_is_immutable(service):
    with pytest.raises(ValueError):
        service.register(Experiment("checkout-v2","a-different-salt-123"))


def test_assignment_is_immutable(service):
    assert service.assign("checkout-v2","visitor-1") == service.assign("checkout-v2","visitor-1")


def test_ingest_idempotent(service):
    assert service.ingest(event()) is True
    assert service.ingest(event()) is False
    assert len(service.ledger.rows("checkout-v2")) == 1


def test_collision_rejected(service):
    service.ingest(event())
    with pytest.raises(ValueError,match="collision"):
        service.ingest(event(revenue=12.0))


def test_multiple_outcomes_per_subject_rejected(service):
    service.ingest(event())
    with pytest.raises(ValueError,match="one outcome"):
        service.ingest(event(id="evt-2"))


def test_unknown_experiment(service):
    with pytest.raises(KeyError):
        service.assign("unknown","visitor-1")


def test_invalid_timestamp():
    with pytest.raises(ValueError):
        Outcome("event-1","checkout-v2","visitor-1",1,2,True,False,"2026-10-01")
