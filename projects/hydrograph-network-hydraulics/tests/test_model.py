import pytest
from hydrograph.model import Pipe,Network,from_dict,to_dict

def test_roundtrip(network):assert from_dict(to_dict(network))==network
def test_bad_resistance():
    with pytest.raises(ValueError):Pipe('x','a','b',0)
def test_self_loop():
    with pytest.raises(ValueError):Pipe('x','a','a',1)
def test_disconnected():
    with pytest.raises(ValueError):Network('R',70,{'A':1,'B':1},(Pipe('a','R','A',1),))
def test_unknown_node():
    with pytest.raises(ValueError):Network('R',70,{'A':1},(Pipe('a','R','B',1),))
def test_negative_demand():
    with pytest.raises(ValueError):Network('R',70,{'A':-1},(Pipe('a','R','A',1),))
def test_duplicate_pipe():
    with pytest.raises(ValueError):Network('R',70,{'A':1},(Pipe('a','R','A',1),Pipe('a','R','A',2)))
