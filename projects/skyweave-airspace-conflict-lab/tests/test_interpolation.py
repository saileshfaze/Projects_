from skyweave.models import Fix,Flight
from skyweave.interpolate import at,intervals

def test_midpoint():
    f=Flight('A',(Fix(0,40,-74,10000),Fix(100,42,-72,12000)))
    p=at(f,50);assert (p.lat,p.lon,p.alt_ft)==(41,-73,11000)
def test_no_extrapolation():
    f=Flight('A',(Fix(0,40,-74,10000),Fix(100,42,-72,12000)))
    assert at(f,-1) is None and at(f,101) is None
def test_segment_count():
    f=Flight('A',(Fix(0,0,0,0),Fix(1,0,0,0),Fix(2,0,0,0)))
    assert len(intervals(f))==2
