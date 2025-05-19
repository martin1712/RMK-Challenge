from math import radians, sin, cos, sqrt, atan2

ZOO_COORD = (59.42643, 24.65805)
TOOMPARK_COORD = (59.43682, 24.73333)
ZONE_RADIUS_M = 75


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.

    Args:
        lat1 (float): Latitude of the first point in decimal degrees.
        lon1 (float): Longitude of the first point in decimal degrees.
        lat2 (float): Latitude of the second point in decimal degrees.
        lon2 (float): Longitude of the second point in decimal degrees.

    Returns:
        float: Distance between the points in meters.
    """
    R = 6371000
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def is_in_zone(lat: float, lon: float, center: tuple, radius: float = ZONE_RADIUS_M) -> bool:
    """
    Check whether a point lies within a certain radius from a center point.

    Args:
        lat (float): Latitude of the point to check.
        lon (float): Longitude of the point to check.
        center (tuple): Tuple of (latitude, longitude) for the center point.
        radius (float, optional): Radius in meters. Defaults to ZONE_RADIUS_M.

    Returns:
        bool: True if the point is within the radius, False otherwise.
    """
    return haversine(lat, lon, center[0], center[1]) <= radius


def is_at_zoo(lat: float, lon: float) -> bool:
    """
    Check whether the point is within the Zoo's geofence.

    Args:
        lat (float): Latitude of the point.
        lon (float): Longitude of the point.

    Returns:
        bool: True if inside the Zoo area, False otherwise.
    """
    return is_in_zone(lat, lon, ZOO_COORD)
