import pytest
from schemaharbor.contracts import Contract

def make(fields): return Contract.from_dict({"name":"orders","version":"1.0.0","fields":fields})

def test_empty(): assert make([]).fields == ()
def test_duplicate():
    with pytest.raises(ValueError): make([{"name":"x","kind":"string"}]*2)
def test_bad_type():
    with pytest.raises(ValueError): make([{"name":"x","kind":"array"}])
def test_bad_bounds():
    with pytest.raises(ValueError): make([{"name":"x","kind":"integer","minimum":4,"maximum":2}])
def test_unknown_key():
    with pytest.raises(ValueError): Contract.from_dict({"name":"x","version":"1","fields":[],"foo":2})
