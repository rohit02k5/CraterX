import numpy as np

def calculate_roi_area_km2(radius_meters):
    """
    Calculates the area of a circular ROI in square kilometers.
    """
    area_m2 = np.pi * (radius_meters**2)
    return area_m2 / 1_000_000.0

def is_in_roi(crater, roi_center, roi_radius_meters, pixel_scale):
    """
    Checks if a crater is within the circular Landing Zone ROI.
    """
    cx_roi, cy_roi = roi_center
    cx_c, cy_c = crater[:2]
    
    dist_px = np.sqrt((cx_roi - cx_c)**2 + (cy_roi - cy_c)**2)
    dist_m = dist_px * pixel_scale
    
    return dist_m <= roi_radius_meters
