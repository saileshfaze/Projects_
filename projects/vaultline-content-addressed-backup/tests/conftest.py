from pathlib import Path
import pytest
from vaultline.engine import Vault

@pytest.fixture
def sample(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "alpha.txt").write_text("a" * 12000)
    (source / "beta.txt").write_text("a" * 12000)
    (source / "empty.txt").write_bytes(b"")
    (source / "nested").mkdir()
    (source / "nested" / "delta.bin").write_bytes(bytes(range(256)) * 80)
    return tmp_path, source, Vault(tmp_path / "vault")
