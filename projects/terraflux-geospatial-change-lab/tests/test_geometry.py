import numpy as np
from terraflux.geometry import components, cell_geometry, feature_collection


def test_diagonal_connectivity():
    mask = np.eye(4, dtype=bool)
    assert len(components(mask)) == 1
    assert len(components(mask)[0]) == 4


def test_minimum_component_filter():
    mask = np.zeros((5,5), dtype=bool)
    mask[0,0] = True
    mask[3,3:5] = True
    assert [len(x) for x in components(mask, 2)] == [2]


def test_pixel_runs_preserve_exact_area():
    geometry = cell_geometry([(0,0), (0,1), (1,1)], (0,10,0,0,0,-10))
    assert geometry['type'] == 'MultiPolygon'
    assert len(geometry['coordinates']) == 2


def test_feature_areas():
    features = feature_collection([[(0,0), (0,1)]], (0,10,0,0,0,-10), np.ones((2,2)))
    assert features['features'][0]['properties']['area_m2'] == 200
