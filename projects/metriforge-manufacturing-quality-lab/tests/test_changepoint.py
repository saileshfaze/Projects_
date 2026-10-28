import pytest
from metriforge.changepoint import best_split

def test_detects_step():
    result=best_split([0]*20+[5]*20);assert result['index']==20 and result['relative_gain']>0.99
def test_too_short(): assert best_split([1,2,3]) is None
def test_invalid_min():
    with pytest.raises(ValueError):best_split([1]*20,min_segment=1)
