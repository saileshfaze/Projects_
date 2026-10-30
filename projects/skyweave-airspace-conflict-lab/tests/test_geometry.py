from math import isclose
from skyweave.geometry import project,distance_nm,NM_M,FT_M,dot

def test_projection_origin():assert project(40,-74,40,-74)==(0,0)
def test_one_degree_latitude():
    assert 110000<project(41,-74,40,-74)[1]<112000
def test_dateline_short_delta():
    assert abs(project(0,-179.9,0,179.9)[0])<30000
def test_distance():assert isclose(distance_nm((0,0),(1852,0)),1)
def test_units():assert NM_M==1852 and FT_M==0.3048
def test_dot():assert dot((2,3),(4,-1))==5
