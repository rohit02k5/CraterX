import numpy as np
import cv2

def detect_lowlights(img, min_area=5, contrast_limit=47, min_diameter=3, shadow_percentile=15):
    """
    Performance-optimized shadow detection.
    """
    h, w = img.shape
    thresh_val = np.percentile(img, shadow_percentile) 
    mask = (img <= thresh_val).astype(np.uint8)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    
    lowlights = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_area: continue
            
        x_min, y_min = stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP]
        width, height = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        
        if max(width, height) < min_diameter: continue
        if min(width, height) / max(width, height) < 0.2: continue
            
        # Extract LOCAL mask for this label to avoid full-image ops
        y_max, x_max = y_min + height, x_min + width
        roi_labels = labels[y_min:y_max, x_min:x_max]
        roi_img = img[y_min:y_max, x_min:x_max]
        
        local_mask = (roi_labels == i)
        shadow_mean = np.mean(roi_img[local_mask])
        
        # Local background contrast (Section 2.3.4)
        local_win = int(max(width, height) * 1.5)
        by1, by2 = max(0, y_min - local_win), min(h, y_max + local_win)
        bx1, bx2 = max(0, x_min - local_win), min(w, x_max + local_win)
        local_mean = np.mean(img[by1:by2, bx1:bx2])
        
        if (local_mean - shadow_mean) < contrast_limit:
            continue
            
        # Only now calculate full pixel coords (offset by ROI)
        ys, xs = np.where(local_mask)
        pixels_coords = np.column_stack((ys + y_min, xs + x_min))
        
        cy, cx = int(centroids[i, 1]), int(centroids[i, 0])
        lowlights.append((pixels_coords, (cy, cx)))

    return lowlights


def find_highlight(img, low, guide_dir, guide_dist):
    """
    Scale-aware highlight search avoiding absolute thresholds.
    """
    if guide_dir is None or guide_dist == 0:
        return None

    pixels_coords, (cy, cx) = low
    h, w = img.shape

    # Expected highlight position based on sun vector
    ex_y = cy + guide_dir[1] * guide_dist
    ex_x = cx + guide_dir[0] * guide_dist

    # Search window scales with expected crater size
    win = max(5, int(guide_dist * 0.7))
    y1, y2 = max(0, int(ex_y - win)), min(h, int(ex_y + win))
    x1, x2 = max(0, int(ex_x - win)), min(w, int(ex_x + win))
    
    region = img[y1:y2, x1:x2]
    if region.size == 0: return None

    _, max_val, _, max_loc = cv2.minMaxLoc(region)
    
    # Highlight must be significantly brighter than the shadow (no absolute threshold)
    shadow_val = np.mean(img[pixels_coords[:, 0], pixels_coords[:, 1]])
    if max_val < shadow_val + 40: # Relative DN threshold
        return None

    return (max_loc[1] + y1, max_loc[0] + x1) # 返回(y, x)
