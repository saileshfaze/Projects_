import pytest
from vaultline.manifest import seal, verify, canonical
from vaultline.errors import IntegrityError

def test_canonical_order():
    assert canonical({"b":2,"a":1}) == canonical({"a":1,"b":2})

def test_seal_verify():
    item=seal({"a":1}); verify(item)
    item["a"]=2
    with pytest.raises(IntegrityError): verify(item)

def test_missing_digest():
    with pytest.raises(IntegrityError): verify({"a":1})
