"""
Utility functions for the Lunar Crater Detection System.
"""

import numpy as np
from typing import Tuple

def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculates Euclidean distance between two points.
    
    Args:
        p1: (y, x) coordinate.
        p2: (y, x) coordinate.
        
    Returns:
        The distance between the points.
    """
    return float(np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2))

def normalize_vector(v: np.ndarray) -> np.ndarray:
    """
    Normalizes a vector to unit length.
    
    Args:
        v: Input numpy array.
        
    Returns:
        Unit vector.
    """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def setup_logging(log_level: str = "INFO"):
    """
    Sets up basic logging configuration.
    
    Args:
        log_level: Desired log level (e.g., "DEBUG", "INFO").
    """
    import logging
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    print(f"Logging set to {log_level}")

def log_progress(message: str):
    """
    Logs a progress message.
    
    Args:
        message: The message to log.
    """
    print(f"[PROGRESS] {message}")
