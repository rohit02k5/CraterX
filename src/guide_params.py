import numpy as np
import cv2

def compute_guide_params(img, lowlights):
    directions = []
    distances = []

    for low in lowlights[:100]: # Check more
        coords, center = low
        y, x = int(center[0]), int(center[1])
        h, w = img.shape

        y1, y2 = max(0, y-30), min(h, y+30)
        x1, x2 = max(0, x-30), min(w, x+30)
        region = img[y1:y2, x1:x2]
        
        if region.size == 0:
            continue

        _, max_val, _, max_loc = cv2.minMaxLoc(region)
        if max_val > 150:
            dy = max_loc[1] - (y - y1)
            dx = max_loc[0] - (x - x1)
            directions.append((dx, dy))
            distances.append(np.sqrt(dx**2 + dy**2))

    if not directions:
        return (0.0, 0.0), 0.0
        
    avg_dir = np.median(directions, axis=0) # Use median for robustness
    avg_dist = np.median(distances)

    return avg_dir, avg_dist
