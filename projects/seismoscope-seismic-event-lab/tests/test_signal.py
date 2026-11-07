import pytest
from seismoscope.signal import characteristic,detect

def test_constant():assert max(characteristic([1.0]*200))==pytest.approx(1)
def test_zero():assert not any(characteristic([0]*200))
def test_spike():assert max(characteristic([0.01]*120+[10]*10))>5
def test_invalid_window():
    with pytest.raises(ValueError):characteristic([1],5,5)
def test_nonfinite():
    with pytest.raises(ValueError):characteristic([float('nan')])
def test_detect_pulse():assert detect([.01]*120+[2]*10+[.01]*100,'X',50,threshold=3)
def test_bad_hz():
    with pytest.raises(ValueError):detect([1], 'X',0)
