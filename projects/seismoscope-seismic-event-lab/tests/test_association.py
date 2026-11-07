import pytest
from seismoscope.associate import associate
from seismoscope.models import Pick,Station

def test_group():
    p=[Pick('A',1,3),Pick('B',2,3),Pick('C',3,3)]
    assert len(associate(p))==1
def test_reject_two():assert associate([Pick('A',1,3),Pick('B',2,3)])==[]
def test_reject_bad_window():
    with pytest.raises(ValueError):associate([],window_s=0)
def test_station_validation():
    with pytest.raises(ValueError):Station('',0,0)
def test_pick_validation():
    with pytest.raises(ValueError):Pick('A',0,-1)
