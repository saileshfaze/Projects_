"""Test fixtures with a deterministic system clock."""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from chronos_ledger.service import Ledger  # noqa: E402


class Clock:
    def __init__(self):
        self.value = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def __call__(self):
        return self.value

    def set(self, value):
        self.value = datetime.fromisoformat(value.replace("Z", "+00:00"))


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def ledger(tmp_path, clock):
    return Ledger(str(tmp_path / "ledger.sqlite3"), clock=clock)
