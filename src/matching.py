import numpy as np
import cv2

def register_images_global(img1, img2):
    """
    Computes global translation offset using Phase Correlation (Section 2.5).
    """
    if img1.shape != img2.shape:
        # Pad or crop to match for phase correlate
        h = min(img1.shape[0], img2.shape[1])
        w = min(img1.shape[1], img2.shape[1])
        i1, i2 = img1[:h, :w], img2[:h, :w]
    else:
        i1, i2 = img1, img2
        
    shift, response = cv2.phaseCorrelate(i1.astype(np.float32), i2.astype(np.float32))
    return shift # (dx, dy)

def match_craters_multi_view_optimized(all_craters_lists, thumbnails, thumb_scale=0.05):
    """
    Certifies craters across images using thumbnails for global registration.
    """
    if len(all_craters_lists) < 2: return []

    certified = []
    # Use image 0 as ref
    ref_list = all_craters_lists[0]
    ref_thumb = thumbnails[0]
    
    for c1 in ref_list:
        match_count = 1
        for i in range(1, len(all_craters_lists)):
            other_list = all_craters_lists[i]
            other_thumb = thumbnails[i]
            
            # 1. Global Offset from thumbnails
            dx_t, dy_t = register_images_global(ref_thumb, other_thumb)
            dx_glob, dy_glob = dx_t / thumb_scale, dy_t / thumb_scale
            
            # 2. Local Correction
            loc_dx, loc_dy = compute_local_registration_offset(c1[0] + dx_glob, c1[1] + dy_glob, other_list)
            
            # 3. Match
            target = (c1[0] + dx_glob + loc_dx, c1[1] + dy_glob + loc_dy, c1[2])
            if is_robust_match(target, other_list):
                match_count += 1
                
        if match_count >= 2:
            certified.append(c1)
            
    return certified

def compute_local_registration_offset(cx, cy, others):
    offsets = []
    for c2 in others:
        dist = np.sqrt((cx - c2[0])**2 + (cy - c2[1])**2)
        if dist < 100: # Search neighborhood
            offsets.append((c2[0] - cx, c2[1] - cy))
    if not offsets: return 0, 0
    return np.median(offsets, axis=0)

def is_robust_match(c1, others):
    cx1, cy1, d1 = c1[:3]
    for c2 in others:
        cx2, cy2, d2 = c2[:3]
        dist = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
        pos_tol = max(4.0, 0.15 * d1)
        if dist < pos_tol and abs(d1 - d2) < 0.2 * d1:
            return True
    return False
