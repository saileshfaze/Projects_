import pytest
from vaultline.paths import safe_relative, safe_target
from vaultline.errors import VaultlineError

@pytest.mark.parametrize("raw", ["", "../bad", "a/../b", "/absolute", "a//b", "a/./b", "C:/win", "a\\b", "a\x00b"])
def test_reject(raw):
    with pytest.raises(VaultlineError): safe_relative(raw)

@pytest.mark.parametrize("raw", ["x.txt", "a/b/c.csv", "emoji.txt"])
def test_allow(raw):
    assert safe_relative(raw).as_posix() == raw

def test_symlink_parent(tmp_path):
    target=tmp_path/"target"; target.mkdir(); (target/"link").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(VaultlineError): safe_target(target,"link/file.txt")

def test_symlink_file(tmp_path):
    target=tmp_path/"target"; target.mkdir(); (target/"x").symlink_to(tmp_path/"other")
    with pytest.raises(VaultlineError): safe_target(target,"x")
