import pytest
from vaultline.errors import VaultlineError

def test_prune_dry_run(sample):
    root, source, vault=sample
    a=vault.snapshot(source)
    (source/"alpha.txt").write_text("new" * 2000)
    b=vault.snapshot(source)
    result=vault.prune(keep=1, dry_run=True)
    assert result["removed_snapshots"] == 1
    assert len(vault.list_snapshots()) == 2
    assert vault.load(a["id"])

def test_prune_apply(sample):
    root, source, vault=sample
    a=vault.snapshot(source)
    (source/"alpha.txt").write_text("new" * 2000)
    b=vault.snapshot(source)
    result=vault.prune(keep=1, dry_run=False)
    assert result["removed_snapshots"] == 1
    assert len(vault.list_snapshots()) == 1
    assert vault.verify(b["id"])["ok"]

def test_prune_all(sample):
    root, source, vault=sample
    vault.snapshot(source)
    vault.prune(keep=0, dry_run=False)
    assert vault.stats()["snapshots"] == 0
    assert vault.stats()["objects"] == 0

def test_bad_keep(sample):
    root, source, vault=sample
    for keep in [-1, 1.5, "2"]:
        with pytest.raises(VaultlineError): vault.prune(keep)
