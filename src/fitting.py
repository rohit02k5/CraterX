import numpy as np

import numpy as np
# Assuming config is available or we pass the scale
from config import PIXEL_SIZE_METERS

def fit_crater(img, low, highlight_pt):
    """
    Refines crater center and diameter using iterative contrast-maximization.
    Returns (cx, cy, d_meters) or None if no valid fit.
    """
    pixels_coords, (cy_low, cx_low) = low
    hy, hx = highlight_pt
    
    # Initial guess: center is between shadow and highlight
    cx = (cx_low + hx) / 2
    cy = (cy_low + hy) / 2
    d_initial = np.sqrt((hx - cx_low)**2 + (hy - cy_low)**2)
    
    best_cx, best_cy, best_d = cx, cy, d_initial
    best_score = -1.0 # Rejection floor
    
    sun_dir = np.array([hx - cx_low, hy - cy_low], dtype=np.float32)
    sun_norm = np.linalg.norm(sun_dir)
    if sun_norm == 0: return None
    sun_dir /= sun_norm

    # Search window for refinement
    # Paper uses 0.5px for center and 1px for diameter
    for dd in np.arange(max(3, d_initial - 4), d_initial + 5, 1): 
        r = dd / 2
        for dx in np.arange(-2, 2.5, 0.5):
            for dy in np.arange(-2, 2.5, 0.5):
                nx, ny = cx + dx, cy + dy
                score = evaluate_contrast_fast(img, nx, ny, r, sun_dir)
                if score > best_score:
                    best_score = score
                    best_cx, best_cy, best_d = nx, ny, dd
                    
    # Rejection Gate: if the best score is still below a noise floor, discard
    # This prevents "pure noise" from becoming a crater.
    if best_score < 10: # DN contrast floor
        return None
        
    # Return 4-tuple: (cx, cy, d_meters, freshness=None) 
    # Conversion to meters happens here for scientific consistency.
    return (best_cx, best_cy, best_d * PIXEL_SIZE_METERS, None)


def evaluate_contrast_fast(img, cx, cy, r, sun_dir):
    """
    Vectorized contrast evaluation.
    """
    h, w = img.shape
    if r < 1: return -1.0
    
    y_min, y_max = max(0, int(cy - r)), min(h, int(cy + r))
    x_min, x_max = max(0, int(cx - r)), min(w, int(cx + r))
    
    if y_max <= y_min or x_max <= x_min: return -1.0
    
    region = img[y_min:y_max, x_min:x_max]
    y_grid, x_grid = np.ogrid[y_min:y_max, x_min:x_max]
    
    dist_sq = (x_grid - cx)**2 + (y_grid - cy)**2
    mask = dist_sq <= r**2
    if not np.any(mask): return -1.0
    
    dots = (x_grid - cx) * sun_dir[0] + (y_grid - cy) * sun_dir[1]
    
    lighter_pixels = region[mask & (dots > 0)]
    darker_pixels = region[mask & (dots <= 0)]
    
    if lighter_pixels.size == 0 or darker_pixels.size == 0:
        return -1.0
    
    return np.mean(lighter_pixels) - np.mean(darker_pixels)
