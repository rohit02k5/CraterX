# Configuration and Hyperparameters for Lunar Crater Detection

# --- Camera & Sensor ---
PIXEL_SIZE_METERS = 0.5 # Native LROC NAC resolution restored

# --- Processing Constraints ---
STRIP_SIZE = (2000, 2000)
STRIP_OVERLAP = 200       # Overlap in pixels

# --- ROI & Science Area ---
ROI_CENTER_X = 500
ROI_CENTER_Y = 500
ROI_RADIUS_METERS = 500

# --- Detection Parameters ---
CONTRAST_LIMIT = 47
MIN_DIAMETER_PIXELS = 3
SHADOW_PERCENTILE = 15

# --- Matching & Certification ---
MATCHING_TOLERANCE_PX = 6.0
MIN_VIEWS_FOR_CERT = 2

# LROC NAC METADATA MAPPING (FOR OPTIMIZATION)
IMAGE_METADATA = {
    "M127159138": {"angle": 65.29, "dir": "W", "scale": 0.50},
    "M135418902": {"angle": 46.42, "dir": "E", "scale": 0.40},
    "M150749234": {"angle": 65.31, "dir": "W", "scale": 0.40},
    "M175502049": {"angle": 57.78, "dir": "E", "scale": 0.35},
    "synthetic_0": {"angle": 65.0, "dir": "W", "scale": 0.50},
    "synthetic_1": {"angle": 65.0, "dir": "W", "scale": 0.50},
    "synthetic_2": {"angle": 65.0, "dir": "W", "scale": 0.50},
    "synthetic_3": {"angle": 65.0, "dir": "W", "scale": 0.50},
}
