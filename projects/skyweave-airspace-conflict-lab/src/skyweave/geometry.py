"""Local tangent-plane projection; appropriate for regional synthetic tracks."""
from math import cos, radians, sqrt
R_EARTH_M = 6371008.8
NM_M = 1852.0
FT_M = 0.3048

def project(lat: float, lon: float, ref_lat: float, ref_lon: float) -> tuple[float,float]:
    """Return east/north metres. Not a global geodesic projection."""
    dlon = (lon-ref_lon+180.0)%360.0-180.0
    return (R_EARTH_M*radians(dlon)*cos(radians(ref_lat)),R_EARTH_M*radians(lat-ref_lat))

def distance_nm(a:tuple[float,float],b:tuple[float,float])->float:
    return sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)/NM_M

def dot(a:tuple[float,float],b:tuple[float,float])->float:
    return a[0]*b[0]+a[1]*b[1]
