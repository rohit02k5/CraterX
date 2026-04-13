import numpy as np

def extract_patch(img, cx, cy, d):
    cx, cy = int(cx), int(cy)
    r = int(d) // 2
    if r < 1: r = 1
    
    y_min, y_max = cy - r, cy + r
    x_min, x_max = cx - r, cx + r
    
    h, w = img.shape
    patch = np.zeros((2*r, 2*r), dtype=img.dtype) + int(np.mean(img))
    
    # Calculate valid slice in image
    iy_min, iy_max = max(0, y_min), min(h, y_max)
    ix_min, ix_max = max(0, x_min), min(w, x_max)
    
    # Calculate valid slice in patch
    py_min = max(0, -y_min)
    py_max = py_min + (iy_max - iy_min)
    px_min = max(0, -x_min)
    px_max = px_min + (ix_max - ix_min)
    
    if iy_max > iy_min and ix_max > ix_min:
        patch[py_min:py_max, px_min:px_max] = img[iy_min:iy_max, ix_min:ix_max]
        
    return patch


FRESHNESS_CLASSES = ["Prominent", "Sharp", "Distinct", "Faint", "Vague"]

def classify_freshness(patch):
    """
    Classifies a crater patch into one of five freshness classes (Section 2.4).
    Based on the standard deviation and max contrast within the patch.
    """
    if patch.size == 0: return "Vague"
    
    std = np.std(patch)
    # Normed contrast between center and rim
    # For a simple heuristic: standard deviation is a good proxy for 'sharpness'
    if std > 60: return "Prominent"
    if std > 45: return "Sharp"
    if std > 30: return "Distinct"
    if std > 15: return "Faint"
    return "Vague"


def build_class_templates(craters, img):
    """
    Builds a library of templates grouped by diameter and freshness class.
    """
    templates = {cls: {} for cls in FRESHNESS_CLASSES}

    for c in craters:
        cx, cy, d = c
        d_int = int(d)
        if d_int % 2 != 0: d_int += 1
        
        patch = extract_patch(img, cx, cy, d_int)
        freshness = classify_freshness(patch)

        if d_int not in templates[freshness]:
            templates[freshness][d_int] = []

        templates[freshness][d_int].append(patch)

    final_templates = {cls: {} for cls in FRESHNESS_CLASSES}
    for cls in FRESHNESS_CLASSES:
        for d in templates[cls]:
            shape = templates[cls][d][0].shape
            valid_patches = [p for p in templates[cls][d] if p.shape == shape]
            if valid_patches:
                final_templates[cls][int(d)] = np.mean(valid_patches, axis=0)

    return final_templates


def refine_with_freshness_templates(craters, class_templates, img):
    """
    Refines crater positions using the class-specific templates.
    """
    import cv2
    refined = []

    for c in craters:
        cx, cy, d = c
        d_int = int(d)
        
        # Determine freshness to pick the right template
        temp_patch = extract_patch(img, cx, cy, d_int)
        freshness = classify_freshness(temp_patch)

        if d_int not in class_templates[freshness]:
            # Try nearest freshness if exact match not found? 
            # Or just fall back to generic
            refined.append((*c, freshness))
            continue

        template = class_templates[freshness][d_int]
        win = 5
        cx_i, cy_i = int(cx), int(cy)
        r = d_int // 2
        
        y_min, y_max = max(0, cy_i - r - win), min(img.shape[0], cy_i + r + win)
        x_min, x_max = max(0, cx_i - r - win), min(img.shape[1], cx_i + r + win)
        
        search_area = img[y_min:y_max, x_min:x_max]
        if search_area.shape[0] < template.shape[0] or search_area.shape[1] < template.shape[1]:
            refined.append((*c, freshness))
            continue
            
        res = cv2.matchTemplate(search_area.astype(np.uint8), template.astype(np.uint8), cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        
        new_cx = x_min + max_loc[0] + r
        new_cy = y_min + max_loc[1] + r
        
        refined.append((new_cx, new_cy, d, freshness))

    return refined
