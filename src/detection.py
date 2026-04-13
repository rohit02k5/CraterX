import numpy as np
import cv2

def detect_lowlights(img, min_area=5, contrast_limit=47):
    """
    Detects lowlight regions (shadows) and filters them based on a contrast limit.
    """
    # Threshold for dark regions (lowlights)
    # The paper mentions scanning for dark areas below a threshold.
    # We use a percentile to adapt to image normalization.
    thresh_val = np.percentile(img, 15) 
    mask = img <= thresh_val
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
    
    lowlights = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_area:
            continue
            
        # Get pixels for this label
        mask_i = (labels == i)
        pixels = img[mask_i]
        
        # Contrast limit check (Paper Section 2.3.4)
        # Craters with very low contrast are likely noise or too faint.
        local_mean = np.mean(img[max(0, int(centroids[i][1]-10)):min(img.shape[0], int(centroids[i][1]+10)),
                                 max(0, int(centroids[i][0]-10)):min(img.shape[1], int(centroids[i][0]+10))])
        local_contrast = local_mean - np.mean(pixels)
        
        if local_contrast < contrast_limit:
            continue

        contours, _ = cv2.findContours(mask_i.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: continue
        
        cnt = contours[0]
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0: continue
        
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        centroid = centroids[i]  # (cx, cy)
        
        if circularity > 0.2: # Paper allows slightly irregular shapes for small craters
            lowlights.append((np.column_stack(np.where(mask_i)), (centroid[1], centroid[0])))

    return lowlights


def find_highlight(img, low, guide_dir, guide_dist):
    """
    Finds the corresponding sunlit rim (highlight) for a given shadow.
    """
    _, (cy, cx) = low
    h, w = img.shape

    try:
        gnorm = np.linalg.norm(guide_dir)
    except:
        return None
        
    if gnorm == 0:
        return None
        
    # Expected highlight position
    ex_x = cx + (guide_dir[0] / gnorm) * guide_dist
    ex_y = cy + (guide_dir[1] / gnorm) * guide_dist

    # Search window (Section 2.2.3)
    # The search window size should be proportional to the expected distance
    win = max(5, int(guide_dist * 0.5))
    y_min, y_max = max(0, int(ex_y - win)), min(h, int(ex_y + win))
    x_min, x_max = max(0, int(ex_x - win)), min(w, int(ex_x + win))
    
    search_region = img[y_min:y_max, x_min:x_max]
    if search_region.size == 0:
        return None

    _, max_val, _, max_loc = cv2.minMaxLoc(search_region)
    
    # Paper mentions highlights must be significantly brighter than the shadow and surroundings
    # We use a relative threshold or a fixed high value
    if max_val < 100: 
        return None

    return (max_loc[1] + y_min, max_loc[0] + x_min) # (y, x)
