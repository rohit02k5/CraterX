import numpy as np

def fit_crater(img, low, high):
    low_coords, low_center = low
    hy, hx = high
    
    # Initial guess
    cx = (low_center[1] + hx) / 2
    cy = (low_center[0] + hy) / 2
    d = np.linalg.norm(np.array(low_center) - np.array([hy, hx]))
    
    # Refine guess by looking for edges/rim
    # For now, let's keep the local search but make it more robust
    best = (cx, cy, d)
    best_score = -float('inf')
    
    for dd in np.linspace(0.8*d, 1.5*d, 5):
        for dx in np.linspace(-2, 2, 3):
            for dy in np.linspace(-2, 2, 3):
                nx, ny, nd = cx+dx, cy+dy, dd
                score = evaluate(img, nx, ny, nd)
                if score > best_score:
                    best_score = score
                    best = (nx, ny, nd)
                    
    return best


def evaluate(img, cx, cy, d):
    # A better evaluation looks for shadow on one side and highlight on the other
    # or just a high contrast across the rim
    h, w = img.shape
    r = int(d/2)
    if r < 2: return -1
    
    # Create a mask for the crater
    y, x = np.ogrid[max(0, int(cy-r)):min(h, int(cy+r)), max(0, int(cx-r)):min(w, int(cx+r))]
    mask = (x-cx)**2 + (y-cy)**2 <= r**2
    
    if not np.any(mask): return -1
    
    region = img[max(0, int(cy-r)):min(h, int(cy+r)), max(0, int(cx-r)):min(w, int(cx+r))]
    
    # Contrast measure: variance within the crater (shadow vs highlight should have high variance)
    # Plus the mean should be around the image mean
    return np.std(region[mask])
