# Configuration and Hyperparameters for Lunar Crater Detection

# --- Camera & Sensor ---
PIXEL_SIZE_METERS = 0.5 # LROC NAC standard

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
