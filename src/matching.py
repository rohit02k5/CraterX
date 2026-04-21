import numpy as np
import cv2
from scipy.spatial import cKDTree
from config import MIN_VIEWS_FOR_CERT

def register_images_global(img1, img2):
    """
    Computes global translation offset using Phase Correlation (Section 2.5).
    """
    if img1.shape != img2.shape:
        # Pad or crop to match for phase correlate
        h = min(img1.shape[0], img2.shape[0])
        w = min(img1.shape[1], img2.shape[1])
        i1, i2 = img1[:h, :w], img2[:h, :w]
    else:
        i1, i2 = img1, img2
        
    shift, response = cv2.phaseCorrelate(i1.astype(np.float32), i2.astype(np.float32))
    return shift # (dx, dy)

def match_craters_multi_view_optimized(all_craters_lists, thumbnails, thumb_scale=0.05):
    """
    Certifies craters across images using thumbnails for global registration.
    Uses a UNION set approach: any candidate matched in >=2 images is certified.
    """
    if len(all_craters_lists) < 2: return []

    certified = []
    
    # Pre-build KD-Trees for ultra-fast spatial querying
    trees = []
    for lst in all_craters_lists:
        if len(lst) > 0:
            # Create a 2D array of (cx, cy) for KDTree
            pts = np.array([[c[0], c[1]] for c in lst], dtype=np.float32)
            trees.append(cKDTree(pts))
        else:
            trees.append(None)
            
    # 1. Gather all unique candidates from ALL images
    # We'll use image 0 as our coordinate frame for the final catalog
    ref_thumb = thumbnails[0]
    
    # Track which candidates are already accounted for to avoid duplicates in the union
    certified_mask_indices = [set() for _ in range(len(all_craters_lists))]

    # Pre-compute all relative offsets once
    global_offsets = []
    for thumb in thumbnails:
        dx, dy = register_images_global(ref_thumb, thumb)
        global_offsets.append((dx / thumb_scale, dy / thumb_scale))

    for i in range(len(all_craters_lists)):
        curr_list = all_craters_lists[i]
        curr_thumb = thumbnails[i]
        
        # Global offset from ref to current
        dx_t, dy_t = register_images_global(ref_thumb, curr_thumb)
        dx_glob, dy_glob = dx_t / thumb_scale, dy_t / thumb_scale
        
        for idx, c1 in enumerate(curr_list):
            if idx in certified_mask_indices[i]: continue
            
            match_count = 1
            matched_indices = [(i, idx)]
            
            # Check other images
            for j in range(len(all_craters_lists)):
                if i == j: continue
                other_list = all_craters_lists[j]
                
                # Relative offset i -> j (Precomputed)
                dx_ref_j, dy_ref_j = global_offsets[j]
                
                # Transform c1 to image j coords
                # c1_in_ref = c1 - dx_glob_i
                # c1_in_j = c1_in_ref + dx_glob_j
                tx, ty = c1[0] - dx_glob + dx_ref_j, c1[1] - dy_glob + dy_ref_j
                
                # Local correction and robust match using pre-built KDTree
                loc_dx, loc_dy = compute_local_registration_offset(tx, ty, trees[j], other_list)
                target = (tx + loc_dx, ty + loc_dy, c1[2])
                
                m_idx = find_robust_match_index(target, trees[j], other_list)
                if m_idx is not None:
                    match_count += 1
                    matched_indices.append((j, m_idx))
            
            if match_count >= MIN_VIEWS_FOR_CERT:
                # Use ref-frame coords for output
                c_ref = [c1[0] - dx_glob, c1[1] - dy_glob, c1[2], c1[3], i]
                certified.append(c_ref)
                # Mark as used across all images
                for img_j, idx_j in matched_indices:
                    certified_mask_indices[img_j].add(idx_j)
            
    return certified

def find_robust_match_index(c1, others_tree, others_data):
    if others_tree is None: return None
    cx1, cy1, d1 = c1[:3]
    pos_tol = max(4.0, 0.15 * d1)
    
    # O(log N) fast spatial query
    indices = others_tree.query_ball_point((cx1, cy1), pos_tol)
    
    for idx in indices:
        c2 = others_data[idx]
        d2 = c2[2]
        if abs(d1 - d2) < 0.2 * d1:
            return idx
    return None

def compute_local_registration_offset(cx, cy, others_tree, others_data):
    if others_tree is None: return 0, 0
    
    # O(log N) fast spatial query
    indices = others_tree.query_ball_point((cx, cy), 100)
    
    offsets = []
    for idx in indices:
        c2 = others_data[idx]
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
