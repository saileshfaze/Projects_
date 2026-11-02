import pytest
from vaultline.objects import ObjectStore
from vaultline.errors import IntegrityError, VaultlineError

def test_dedup(tmp_path):
    store=ObjectStore(tmp_path)
    a=store.put(b"payload"); b=store.put(b"payload")
    assert a == b and store.get(a) == b"payload"
    assert list(store.all_digests()) == [a]

def test_corruption(tmp_path):
    store=ObjectStore(tmp_path); digest=store.put(b"ok")
    store.path(digest).write_bytes(b"bad")
    with pytest.raises(IntegrityError): store.get(digest)
    with pytest.raises(IntegrityError): store.put(b"ok")

def test_missing(tmp_path):
    store=ObjectStore(tmp_path); digest=store.put(b"x"); store.remove(digest)
    with pytest.raises(IntegrityError): store.get(digest)

def test_invalid_hash(tmp_path):
    store=ObjectStore(tmp_path)
    for digest in ["", "xyz", "a"*63, "A"*64, "../" + "a"*61]:
        with pytest.raises(VaultlineError): store.path(digest)

def test_empty_object(tmp_path):
    store=ObjectStore(tmp_path); digest=store.put(b"")
    assert store.get(digest) == b""

def test_symlink_object(tmp_path):
    store=ObjectStore(tmp_path); digest=store.put(b"abc")
    path=store.path(digest); path.unlink(); path.symlink_to(tmp_path/"outside")
    with pytest.raises(IntegrityError): store.get(digest)
