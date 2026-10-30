from skyweave.reporting import geojson,conflict_csv,timeline_svg
from skyweave.detector import detect

def test_geojson(crossing_flights):
    data=geojson(crossing_flights)
    assert data['type']=='FeatureCollection' and len(data['features'])==4
    assert data['features'][0]['geometry']['coordinates'][0][0]==-74.06

def test_csv(crossing_flights):
    csv=conflict_csv(detect(crossing_flights))
    assert csv.startswith('a,b,entry_s') and 'SW101' in csv

def test_svg(crossing_flights):
    svg=timeline_svg(detect(crossing_flights))
    assert svg.startswith('<svg') and 'SW101' in svg

def test_empty_svg():assert 'svg' in timeline_svg([])
