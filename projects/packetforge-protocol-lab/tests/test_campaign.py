import random
import pytest
from packetforge.campaign import run
from packetforge.mutate import mutate

def test_determinism(): assert run(123,100)==run(123,100)
def test_counts():
    r=run(2026,250)
    assert r.accepted+r.rejected+r.unexpected==250
    assert sum(r.by_operation.values())==250
    assert r.unexpected==0

def test_empty(): assert run(1,0).cases==0
@pytest.mark.parametrize('count',[-1,100001])
def test_bounds(count):
    with pytest.raises(ValueError):run(1,count)
def test_mutations():
    rng=random.Random(123)
    changes=[mutate(b'hello world',rng) for _ in range(200)]
    assert {c.operation for c in changes}=={'flip','truncate','insert','duplicate','zero'}
def test_empty_mutation(): assert mutate(b'',random.Random(1)).data
