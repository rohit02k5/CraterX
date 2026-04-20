"""
Utility functions for the Lunar Crater Detection System.
"""
import numpy as np
from typing import Tuple

def haversine_distance(p1: Tuple[float, float], p2: Tuple[float, float], radius=1737400) -> float:
    """
    Calculates the great-circle distance between two points on a sphere (e.g. Moon).
    Default radius is the mean radius of the Moon in meters.
    
    Args:
        p1: (lat, lon) or (y, x) if projected.
        p2: (lat, lon) or (y, x) if projected.
        radius: Sphere radius.
        
    Returns:
        Distance in meters.
    """
    phi1, phi2 = np.radians(p1[0]), np.radians(p2[0])
    dphi = np.radians(p2[0] - p1[0])
    dlambda = np.radians(p2[1] - p1[1])
    
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return radius * c

def pixel_to_latlon(px, py, transform):
    """
    Converts pixel coordinates to World Coordinates (Lat/Lon) using an affine transform.
    Requires transform from rasterio.
    """
    if transform is None: return (0.0, 0.0)
    lon, lat = transform * (px, py)
    return lat, lon


def log_progress(message: str):
    """Logs a progress message."""
    print(f"[PROGRESS] {message}")
