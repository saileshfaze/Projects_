from skyweave.models import Flight,Fix,Thresholds
from skyweave.detector import detect,_horizontal_window,_vertical_window

def flight(name,lat1,lon1,lat2,lon2,alt1=30000,alt2=None,start=0,end=600):
    return Flight(name,(Fix(start,lat1,lon1,alt1),Fix(end,lat2,lon2,alt1 if alt2 is None else alt2)))

def test_crossing_detected(crossing_flights):
    result=detect(crossing_flights)
    assert len(result)==1 and (result[0].a,result[0].b)==('SW101','SW202')
    assert result[0].closest_s==300 and result[0].min_horizontal_nm<0.001

def test_separated(separated_flights):assert detect(separated_flights)==[]
def test_vertical_separation():
    a=flight('A',40,-74,40,-73.9,30000)
    b=flight('B',40,-74,40,-73.9,32000)
    assert not detect((a,b))
def test_same_track_conflict():
    a=flight('A',40,-74,40,-73.9)
    b=flight('B',40,-74,40,-73.9)
    result=detect((a,b));assert len(result)==1 and result[0].entry_s==0 and result[0].exit_s==600

def test_no_temporal_overlap():
    a=flight('A',40,-74,40,-73.9)
    b=flight('B',40,-74,40,-73.9,start=601,end=1201)
    assert not detect((a,b))
def test_strict_vertical_boundary():
    a=flight('A',40,-74,40,-73.9,30000)
    b=flight('B',40,-74,40,-73.9,31000)
    assert not detect((a,b))
def test_horizontal_quadratic_window():
    lo,hi=_horizontal_window((-10,0),(1,0),5,20)
    assert (lo,hi)==(5,15)
def test_horizontal_static_inside():assert _horizontal_window((0,0),(0,0),5,10)==(0,10)
def test_horizontal_static_outside():assert _horizontal_window((10,0),(0,0),5,10) is None
def test_horizontal_tangent_not_conflict():assert _horizontal_window((0,5),(1,0),5,10) is None
def test_vertical_window():assert _vertical_window(-10,1,5,20)==(5,15)
def test_vertical_static_inside():assert _vertical_window(0,0,5,10)==(0,10)
def test_vertical_static_outside():assert _vertical_window(6,0,5,10) is None
def test_reversed_input_same_output(crossing_flights):
    assert detect(crossing_flights)==detect(tuple(reversed(crossing_flights)))
def test_empty_input():assert detect(())==[]
def test_multisegment_merges():
    a=Flight('A',(Fix(0,40,-74,30000),Fix(300,40,-74,30000),Fix(600,40,-74,30000)))
    b=Flight('B',(Fix(0,40,-74,30000),Fix(600,40,-74,30000)))
    c=detect((a,b));assert len(c)==1 and c[0].entry_s==0 and c[0].exit_s==600
