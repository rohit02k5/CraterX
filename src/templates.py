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


def build_templates(craters, img):
    templates = {}

    for c in craters:
        cx, cy, d = c
        d_int = int(d)
        if d_int % 2 != 0: d_int += 1 # Ensure even for centering
        
        patch = extract_patch(img, cx, cy, d_int)

        if d_int not in templates:
            templates[d_int] = []

        templates[d_int].append(patch)

    final_templates = {}
    for d in templates:
        # Filter out if somehow shapes still mismatch (shouldn't happen with new extract_patch)
        shape = templates[d][0].shape
        valid_patches = [p for p in templates[d] if p.shape == shape]
        if valid_patches:
            final_templates[int(d)] = np.mean(valid_patches, axis=0)

    return final_templates


def refine_with_templates(craters, templates, img):
    import cv2
    refined = []

    for c in craters:
        cx, cy, d = c
        d_int = int(d)

        if d_int not in templates:
            refined.append(c)
            continue

        template = templates[d_int]
        # Expand search area slightly
        win = 5
        cx_i, cy_i = int(cx), int(cy)
        r = d_int // 2
        
        y_min, y_max = max(0, cy_i - r - win), min(img.shape[0], cy_i + r + win)
        x_min, x_max = max(0, cx_i - r - win), min(img.shape[1], cx_i + r + win)
        
        patch = img[y_min:y_max, x_min:x_max]
        if patch.shape[0] < template.shape[0] or patch.shape[1] < template.shape[1]:
            refined.append(c)
            continue
            
        res = cv2.matchTemplate(patch, template.astype(np.uint8), cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        
        # New center
        new_cx = x_min + max_loc[0] + r
        new_cy = y_min + max_loc[1] + r
        
        refined.append((new_cx, new_cy, d))

    return refined
