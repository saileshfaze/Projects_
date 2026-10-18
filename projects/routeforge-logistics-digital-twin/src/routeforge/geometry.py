"""Geodesic distances for synthetic small-area logistics experiments."""
from math import asin, cos, radians, sin, sqrt, ceil

EARTH_RADIUS_KM = 6371.0088

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = radians(lat1), radians(lat2)
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(p1) * cos(p2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(min(1.0, sqrt(a)))

def travel_minutes(km: float, speed_kmh: float, road_factor: float = 1.35) -> int:
    if km < 0 or speed_kmh <= 0 or road_factor < 1:
        raise ValueError("Invalid travel parameters")
    return ceil(60 * km * road_factor / speed_kmh)
