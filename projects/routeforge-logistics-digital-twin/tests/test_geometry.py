import pytest
from routeforge.geometry import haversine_km, travel_minutes

def test_same_location():
    assert haversine_km(41, 14, 41, 14) == 0

def test_symmetry():
    assert haversine_km(41, 14, 42, 15) == pytest.approx(haversine_km(42, 15, 41, 14))

def test_travel_minutes():
    assert travel_minutes(10, 60, road_factor=1) == 10

def test_invalid_speed():
    with pytest.raises(ValueError):
        travel_minutes(10, 0)
