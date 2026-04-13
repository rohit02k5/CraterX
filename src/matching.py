import numpy as np

def compute_local_registration_offset(c1, others, win=50):
    """
    Simulates the 'XY discrepancy map' concept (Section 2.5.2).
    Finds a local translation offset that maximizes the number of potential matches in a window.
    """
    x1, y1, _ = c1
    offsets = []
    
    for c2 in others:
        x2, y2, _ = c2
        if abs(x1 - x2) < win and abs(y1 - y2) < win:
            offsets.append((x2 - x1, y2 - y1))
            
    if not offsets:
        return 0, 0
        
    # Return the median offset (most consistent translation in the neighborhood)
    return np.median(offsets, axis=0)


def is_robust_match(c1, c2, offset=(0, 0)):
    """
    Checks if two craters match, accounting for local registration offset.
    """
    x1, y1, d1 = c1
    x2, y2, d2 = c2
    
    # Correct x1, y1 by the estimated local offset
    nx1 = x1 + offset[0]
    ny1 = y1 + offset[1]
    
    # Tolerance based on paper (typically a fraction of diameter or few pixels)
    tol = max(4, 0.15 * d1)
    
    return (abs(nx1 - x2) < tol and abs(ny1 - y2) < tol and abs(d1 - d2) < (0.2 * d1))


def match_craters_multi_view(all_craters):
    """
    Matches craters across multiple views and certifies those found in at least 2 images (Section 2.5).
    """
    if not all_craters:
        return []
    if len(all_craters) == 1:
        return all_craters[0]

    certified = []
    
    # Use the first image as the reference for now
    for c1 in all_craters[0]:
        matches_found = 1 # Found in the first image
        
        for i in range(1, len(all_craters)):
            # Compute local registration offset for this crater relative to the other image
            offset = compute_local_registration_offset(c1, all_craters[i])
            
            for c2 in all_craters[i]:
                if is_robust_match(c1, c2, offset):
                    matches_found += 1
                    break
        
        # Paper: Craters must be matched in at least two images to be "certified"
        if matches_found >= 2:
            certified.append(c1)

    return certified
