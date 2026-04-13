import numpy as np

def fit_crater(img, low, high):
    """
    Refines crater center and diameter using an iterative contrast-maximization algorithm.
    Optimized for performance.
    """
    low_coords, low_center = low
    hy, hx = high
    
    # Initial guess: center is between shadow and highlight
    cx = (low_center[1] + hx) / 2
    cy = (low_center[0] + hy) / 2
    d = np.linalg.norm(np.array(low_center) - np.array([hy, hx]))
    
    best_cx, best_cy, best_d = cx, cy, d
    best_score = -float('inf')
    
    # Pre-calculate sun direction
    sun_dir = np.array([hx - low_center[1], hy - low_center[0]])
    sun_norm = np.linalg.norm(sun_dir)
    if sun_norm == 0: return (cx, cy, d)
    sun_dir /= sun_norm

    # Iterative refinement: reduce steps for performance if initial guess is likely good
    # Paper uses 0.5px for center and 1px for diameter.
    # We loop over small window.
    for dd in np.arange(max(2, d - 3), d + 4, 1): # 7 steps
        r = dd / 2
        for dx in np.arange(-2, 2.5, 0.5): # 9 steps
            for dy in np.arange(-2, 2.5, 0.5): # 9 steps
                nx, ny = cx + dx, cy + dy
                score = evaluate_contrast_fast(img, nx, ny, r, sun_dir)
                if score > best_score:
                    best_score = score
                    best_cx, best_cy, best_d = nx, ny, dd
                    
    return (best_cx, best_cy, best_d)


def evaluate_contrast_fast(img, cx, cy, r, sun_dir):
    """
    Faster contrast evaluation using vectorized masking.
    """
    h, w = img.shape
    if r < 1: return -1
    
    y_min, y_max = max(0, int(cy - r)), min(h, int(cy + r))
    x_min, x_max = max(0, int(cx - r)), min(w, int(cx + r))
    
    if y_max <= y_min or x_max <= x_min: return -1
    
    region = img[y_min:y_max, x_min:x_max]
    y_grid, x_grid = np.ogrid[y_min:y_max, x_min:x_max]
    
    dist_sq = (x_grid - cx)**2 + (y_grid - cy)**2
    mask = dist_sq <= r**2
    if not np.any(mask): return -1
    
    # Dot product for lighter/darker half
    dots = (x_grid - cx) * sun_dir[0] + (y_grid - cy) * sun_dir[1]
    
    lighter_pixels = region[mask & (dots > 0)]
    darker_pixels = region[mask & (dots <= 0)]
    
    if lighter_pixels.size == 0 or darker_pixels.size == 0:
        return -1
    
    return np.mean(lighter_pixels) - np.mean(darker_pixels)
