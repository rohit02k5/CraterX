import numpy as np
import cv2

def compute_guide_params(img, lowlights):
    """
    Estimates average sun direction and typical shadow-highlight distance for a strip.
    Uses adaptive logic to match shadows to highlights.
    """
    if not lowlights:
        return None, 0.0

    directions = []
    distances = []
    h, w = img.shape
    
    # Adaptive highlight threshold for this strip
    high_threshold = np.percentile(img, 98)

    for low in lowlights[:100]: # Sample robustly
        _, center = low
        y_c, x_c = int(center[0]), int(center[1])
        
        # Search window for highlight relative to shadow scale
        # Since we don't know the diameter yet, we use a slightly larger window
        win = 40
        y1, y2 = max(0, y_c - win), min(h, y_c + win)
        x1, x2 = max(0, x_c - win), min(w, x_c + win)
        region = img[y1:y2, x1:x2]
        
        if region.size == 0: continue
        
        _, max_val, _, max_loc = cv2.minMaxLoc(region)
        
        if max_val >= high_threshold:
            dx = max_loc[0] - (x_c - x1)
            dy = max_loc[1] - (y_c - y1)
            dist = np.sqrt(dx**2 + dy**2)
            
            # Constraints: highlight must be within a reasonable crater geometry
            if 3 < dist < win:
                directions.append((dx, dy))
                distances.append(dist)
                
    if not directions:
        return None, 0.0
        
    avg_dir_vec = np.median(directions, axis=0)
    avg_dist = np.median(distances)
    
    # Normalize direction
    mag = np.linalg.norm(avg_dir_vec)
    if mag == 0: return None, 0.0
    avg_dir = avg_dir_vec / mag
    
    return avg_dir, avg_dist
