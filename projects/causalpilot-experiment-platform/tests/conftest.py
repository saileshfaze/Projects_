import pytest
from causalpilot.models import Experiment
from causalpilot.service import ExperimentService


@pytest.fixture
def config():
    return Experiment("checkout-v2", "demo-salt-keep-private", minimum_per_arm=5)


@pytest.fixture
def service(tmp_path, config):
    svc = ExperimentService(str(tmp_path / "events.db"))
    svc.register(config)
    return svc
