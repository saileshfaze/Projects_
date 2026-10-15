from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pulsemesh.api import create_app
from pulsemesh.settings import Settings
from pulsemesh.storage import EventStore


@pytest.fixture
def store(tmp_path: Path):
    result = EventStore(tmp_path / "events.sqlite3", allowed_lateness_seconds=3600)
    result.initialize()
    return result


@pytest.fixture
def client(tmp_path: Path):
    app = create_app(Settings(database_path=tmp_path / "api.sqlite3", api_key="test-key"))
    with TestClient(app) as instance:
        yield instance
