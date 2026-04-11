"""
Configuration parameters for the Lunar Crater Detection System.
"""

import os

# Image Paths
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
OUTPUT_DIR = "outputs"

# Thresholds
DETECTION_THRESHOLD = 0.5
MATCHING_TOLERANCE = 10.0  # pixels

# Strip Settings
STRIP_SIZE = (1000, 1000)

# Detection Parameters
CONTRAST_MULTIPLIER = 1.2

# Other Parameters
PIXEL_SIZE_METERS = 1.0  # Scale of the imagery
