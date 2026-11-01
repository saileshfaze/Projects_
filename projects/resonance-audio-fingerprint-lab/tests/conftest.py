import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pytest
from resonance.synthetic import make_clip

@pytest.fixture
def melody():
    return make_clip(7, 3, "melody")

@pytest.fixture
def chirp():
    return make_clip(7, 3, "chirp")
