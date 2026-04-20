import numpy as np
import cv2

def compute_guide_params(img, lowlights, img_path=""):
    """
    Metadata-informed parameter estimation. Skips expensive search loop.
    """
    from config import IMAGE_METADATA
    import os
    
    # Extract ID (e.g., M127159138)
    filename = os.path.basename(img_path).split('.')[0]
    meta = IMAGE_METADATA.get(filename, {"angle": 65, "dir": "W", "scale": 0.5})

    # Convert Direction to Vector
    # Sun from West (W) = Vector points East (+X)
    dx = 1.0 if meta["dir"] == "W" else -1.0
    avg_dir = np.array([dx, 0.0])
    
    # Shadow-to-Diameter ratio from Incidence Angle
    avg_dist = 1.0 / np.tan(np.radians(meta["angle"])) 
    
    return avg_dir, avg_dist
