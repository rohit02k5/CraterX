import numpy as np
import cv2

def detect_lowlights(img, min_area=10):
    # Use Otsu's to find a good threshold for shadows if the image is well-normalized
    # Or use a percentile-based threshold for dark regions
    thresh_val = np.percentile(img, 10) # Heavily dark regions
    mask = img <= thresh_val
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
    
    lowlights = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_area:
            continue
            
        # Get pixels for this label
        mask_i = (labels == i).astype(np.uint8)
        contours, _ = cv2.findContours(mask_i, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours: continue
        cnt = contours[0]
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0: continue
        
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        centroid = centroids[i]  # (cx, cy)
        
        if circularity > 0.3: # Lowered threshold slightly
            lowlights.append((np.column_stack(np.where(labels == i)), (centroid[1], centroid[0])))

    return lowlights


def find_highlight(img, low, guide_dir, guide_dist):
    _, (cy, cx) = low
    h, w = img.shape

    # Calculate search center based on guide direction
    # guide_dir is (dx, dy)
    try:
        gnorm = np.linalg.norm(guide_dir)
    except:
        return None
        
    if gnorm == 0:
        return None
        
    ex_x = cx + (guide_dir[0] / gnorm) * guide_dist
    ex_y = cy + (guide_dir[1] / gnorm) * guide_dist

    # Search window around the expected highlight position
    win = 15
    y_min, y_max = max(0, int(ex_y - win)), min(h, int(ex_y + win))
    x_min, x_max = max(0, int(ex_x - win)), min(w, int(ex_x + win))
    
    search_region = img[y_min:y_max, x_min:x_max]
    if search_region.size == 0:
        return None

    _, max_val, _, max_loc = cv2.minMaxLoc(search_region)
    
    # Only accept if it's significantly brighter than background
    if max_val < 120: # Lowered from 150
        return None

    return (max_loc[1] + y_min, max_loc[0] + x_min) # (y, x)
