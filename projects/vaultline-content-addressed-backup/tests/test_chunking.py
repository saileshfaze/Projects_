import pytest
from vaultline.chunking import chunks, sha256

@pytest.mark.parametrize("size", [0,1,2047,2048,8192,32000,100000])
def test_roundtrip(size):
    data = bytes(range(256)) * (size // 256) + bytes(range(size % 256))
    pieces = list(chunks(data))
    assert b"".join(pieces) == data
    assert all(0 < len(x) <= 32768 for x in pieces)

@pytest.mark.parametrize("args", [(0,8192,32768),(3000,1000,4000),(2048,9000,32768),(2048,8192,4096)])
def test_bad_config(args):
    with pytest.raises(ValueError): list(chunks(b"x", *args))

def test_deterministic():
    data = b"abc123" * 30000
    assert list(chunks(data)) == list(chunks(data))

def test_shifted_content():
    import random
    rng = random.Random(19)
    a = rng.randbytes(150000)
    b = b"xyz" + a
    aa = {sha256(x) for x in chunks(a)}
    bb = {sha256(x) for x in chunks(b)}
    assert len(aa & bb) >= 1
