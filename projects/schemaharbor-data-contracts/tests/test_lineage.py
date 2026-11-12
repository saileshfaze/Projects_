import pytest
from schemaharbor.lineage import impacted

def test_chain(): assert impacted([["a","b"],["b","c"]],"a") == ["b","c"]
def test_diamond(): assert impacted([["a","b"],["a","c"],["b","d"],["c","d"]],"a") == ["b","c","d"]
def test_missing(): assert impacted([["a","b"]],"z") == []
def test_cycle():
 with pytest.raises(ValueError): impacted([["a","b"],["b","a"]],"a")
def test_self():
 with pytest.raises(ValueError): impacted([["a","a"]],"a")
