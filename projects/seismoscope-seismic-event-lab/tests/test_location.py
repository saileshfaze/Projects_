import pytest
from math import hypot
from seismoscope.models import Pick
from seismoscope.synthetic import network
from seismoscope.locate import locate

def test_known_hypocenter():
    stations=network();p=[Pick(c,5+hypot(s.x_km-2,s.y_km+4)/5,4) for c,s in stations.items()]
    e=locate(p,stations)
    assert (e.x_km,e.y_km)==(2,-4)
    assert e.origin_s==pytest.approx(5)
    assert e.residual_s<1e-9

def test_insufficient():
    with pytest.raises(ValueError):locate([Pick('STA_A',1,2)],network())
def test_bad_velocity():
    with pytest.raises(ValueError):locate([],network(),velocity_km_s=0)
def test_bad_bounds():
    with pytest.raises(ValueError):locate([Pick(c,1,2) for c in ['STA_A','STA_B','STA_C']],network(),bounds=(10,0,0,1))
def test_grid_guard():
    with pytest.raises(ValueError):locate([Pick(c,1,2) for c in ['STA_A','STA_B','STA_C']],network(),bounds=(0,1000,0,1000),step_km=.1)
