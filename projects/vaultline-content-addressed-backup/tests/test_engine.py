import json
import pytest
from vaultline.errors import VaultlineError, IntegrityError

def test_snapshot_and_restore(sample):
    root, source, vault=sample
    first=vault.snapshot(source, "baseline")
    assert first["files"] == 4
    assert vault.verify(first["id"])["ok"]
    restored=vault.restore(first["id"], root/"restored")
    assert restored["files"] == 4
    for path in source.rglob("*"):
        if path.is_file(): assert (root/"restored"/path.relative_to(source)).read_bytes() == path.read_bytes()

def test_dedup_across_files(sample):
    root, source, vault=sample
    first=vault.snapshot(source)
    before=vault.stats()["objects"]
    second=vault.snapshot(source)
    assert first["id"] != second["id"]
    assert vault.stats()["objects"] == before

def test_incremental_change(sample):
    root, source, vault=sample
    first=vault.snapshot(source)
    old=vault.stats()["objects"]
    (source/"alpha.txt").write_text("new" * 4000)
    second=vault.snapshot(source)
    assert second["id"] != first["id"]
    assert vault.stats()["objects"] > old

def test_no_overwrite(sample):
    root, source, vault=sample
    first=vault.snapshot(source)
    dest=root/"out"; dest.mkdir(); (dest/"alpha.txt").write_text("existing")
    with pytest.raises(VaultlineError): vault.restore(first["id"], dest)
    assert (dest/"alpha.txt").read_text() == "existing"
    vault.restore(first["id"], dest, overwrite=True)
    assert (dest/"alpha.txt").read_text() == "a" * 12000

def test_corrupt_object_detected(sample):
    root, source, vault=sample
    snap=vault.snapshot(source)
    digest=vault.load(snap["id"])["files"][0]["chunks"][0]
    vault.store.path(digest).write_bytes(b"corrupt")
    with pytest.raises(IntegrityError): vault.verify(snap["id"])
    with pytest.raises(IntegrityError): vault.restore(snap["id"], root/"out")
    assert not (root/"out").exists()

def test_manifest_tampering(sample):
    root, source, vault=sample
    snap=vault.snapshot(source)
    path=vault.manifests/(snap["id"]+".json")
    item=json.loads(path.read_text()); item["label"]="tampered"; path.write_text(json.dumps(item))
    with pytest.raises(IntegrityError): vault.load(snap["id"])

def test_empty_source(sample):
    root, source, vault=sample
    empty=root/"empty"; empty.mkdir()
    snap=vault.snapshot(empty)
    assert snap["files"] == 0
    assert vault.verify(snap["id"])["bytes"] == 0

def test_excludes_symlinks(sample):
    root, source, vault=sample
    (source/"alias.txt").symlink_to(source/"alpha.txt")
    (source/"alias_dir").symlink_to(source/"nested", target_is_directory=True)
    assert vault.snapshot(source)["files"] == 4

def test_source_overlap_rejected(sample):
    root, source, vault=sample
    for path in [root, vault.root, vault.root/"nested"]:
        with pytest.raises(VaultlineError): vault.snapshot(path)

def test_restore_overlap_rejected(sample):
    root, source, vault=sample
    snap=vault.snapshot(source)
    with pytest.raises(VaultlineError): vault.restore(snap["id"], vault.root/"bad")

def test_missing_manifest(sample):
    root, source, vault=sample
    with pytest.raises(IntegrityError): vault.load("a"*64)

def test_bad_label(sample):
    root, source, vault=sample
    with pytest.raises(VaultlineError): vault.snapshot(source, "x"*101)
