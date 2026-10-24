import pytest
from causalpilot.assignment import arm
from causalpilot.models import Experiment


def test_assignment_is_stable(config):
    assert arm(config, "visitor-5") == arm(config, "visitor-5")


def test_assignment_balances_approximately(config):
    ratio=sum(arm(config,f"visitor-{i}")=="B" for i in range(3000))/3000
    assert 0.46 < ratio < 0.54


def test_assignment_changes_with_experiment(config):
    other=Experiment("checkout-v3",config.salt)
    assert any(arm(config,f"visitor-{i}")!=arm(other,f"visitor-{i}") for i in range(50))


def test_invalid_subject_rejected(config):
    with pytest.raises(ValueError):
        arm(config,"bad/subject")


def test_invalid_weights():
    with pytest.raises(ValueError):
        Experiment("valid","valid-long-salt",treatment_fraction=1.2)
