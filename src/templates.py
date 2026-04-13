import numpy as np
import cv2

def extract_patch(img, cx, cy, d):
    """
    Extracts a square patch centered on (cx, cy) with size based on diameter d.
    """
    cx, cy = int(cx), int(cy)
    r = int(d) // 2 + 5 # Add margin
    h, w = img.shape
    
    y1, y2 = max(0, cy - r), min(h, cy + r)
    x1, x2 = max(0, cx - r), min(w, cx + r)
    
    return img[y1:y2, x1:x2]

def classify_freshness(patch, diameter):
    """
    Scale-invariant freshness classification (Section 2.4).
    Uses shadow-highlight contrast ratio normalized by diameter.
    """
    if patch.size == 0 or diameter == 0:
        return "Vague"
        
    # Section 2.4.1: Contrast ratio metric
    min_val, max_val, _, _ = cv2.minMaxLoc(patch)
    contrast = max_val - min_val
    metric = contrast / (diameter + 1e-6) # Normalize by diameter to be scale-invariant
    
    if metric > 25: return "Prominent"
    if metric > 15: return "Sharp"
    if metric > 8: return "Distinct"
    if metric > 4: return "Faint"
    return "Vague"

def build_class_templates(crater_catalog, images):
    """
    Builds the template library by averaging patches from the specific images they originated from.
    """
    # library[freshness][diameter]
    library = {f: {} for f in ["Prominent", "Sharp", "Distinct", "Faint", "Vague"]}
    temp_bins = {f: {} for f in ["Prominent", "Sharp", "Distinct", "Faint", "Vague"]}
    
    # Crater catalog format: (cx, cy, d, freshness, image_idx)
    for c in crater_catalog:
        cx, cy, d, f, img_idx = c
        img = images[img_idx]
        patch = extract_patch(img, cx, cy, d)
        if patch.size == 0: continue
        
        d_bin = int(d)
        patch_resized = cv2.resize(patch, (d_bin+10, d_bin+10))
        
        if d_bin not in temp_bins[f]: temp_bins[f][d_bin] = []
        temp_bins[f][d_bin].append(patch_resized)
        
    for f in temp_bins:
        for db in temp_bins[f]:
            library[f][db] = np.mean(temp_bins[f][db], axis=0).astype(np.float32)
            
    return library

def refine_with_freshness_templates(certified_craters, images, class_templates):
    """
    Refines detection coordinates by matching against class templates.
    """
    refined = []
    for c in certified_craters:
        # Expected input format: (cx, cy, d, freshness, img_idx)
        cx, cy, d, f, img_idx = c
        img = images[img_idx]
        
        template = class_templates.get(f, {}).get(int(d), None)
        if template is not None:
            # Search in a small window
            margin = 5
            patch = extract_patch(img, cx, cy, d + 2*margin)
            if patch.shape[0] >= template.shape[0] and patch.shape[1] >= template.shape[1]:
                res = cv2.matchTemplate(patch.astype(np.float32), template, cv2.TM_CCOEFF_NORMED)
                _, _, _, max_loc = cv2.minMaxLoc(res)
                
                # Update cx, cy based on peak
                cx_ref = cx + (max_loc[0] - margin)
                cy_ref = cy + (max_loc[1] - margin)
                refined.append((cx_ref, cy_ref, d, f))
                continue
        
        refined.append((cx, cy, d, f))
        
    return refined
