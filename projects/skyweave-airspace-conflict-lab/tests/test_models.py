import pytest
from skyweave.models import Fix,Flight,Thresholds,parse_flights,flights_payload
from skyweave.scenarios import crossing

@pytest.mark.parametrize('lat,lon',[(91,0),(-91,0),(0,181),(0,-181)])
def test_bad_coordinates(lat,lon):
    with pytest.raises(ValueError):Fix(0,lat,lon,30000)
@pytest.mark.parametrize('alt',[-1501,100001,float('nan'),float('inf')])
def test_bad_altitude(alt):
    with pytest.raises(ValueError):Fix(0,40,-74,alt)
@pytest.mark.parametrize('callsign',['','abc space','a'*25])
def test_bad_callsign(callsign):
    with pytest.raises(ValueError):Flight(callsign,(Fix(0,0,0,0),Fix(1,0,0,0)))
def test_timestamps_strict():
    with pytest.raises(ValueError):Flight('A',(Fix(0,0,0,0),Fix(0,0,0,0)))
def test_minimum_two_fixes():
    with pytest.raises(ValueError):Flight('A',(Fix(0,0,0,0),))
@pytest.mark.parametrize('h,v',[(0,1000),(5,0),(-1,1000),(float('nan'),1000)])
def test_bad_thresholds(h,v):
    with pytest.raises(ValueError):Thresholds(h,v)
def test_round_trip():
    f=crossing();assert parse_flights(flights_payload(f))==f
def test_duplicate_callsign():
    p=flights_payload(crossing());p['flights'][1]['callsign']=p['flights'][0]['callsign']
    with pytest.raises(ValueError):parse_flights(p)
def test_invalid_payload():
    with pytest.raises(ValueError):parse_flights({})
