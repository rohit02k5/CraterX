import cv2
import numpy as np

MASK_SCALE = 4.0 # Downsample factor for the global flagging mask to save memory

def flag_pixels(mask, crater):
    """
    Marks a crater as detected in a scaled-down global mask.
    crater: (cx, cy, r_pixels)
    """
    cx, cy, r = crater
    # Scale coordinates to the downsampled mask
    cx_s = int(cx / MASK_SCALE)
    cy_s = int(cy / MASK_SCALE)
    r_s = int(r / MASK_SCALE)
    
    # Use uint8 mask to save space (255 = flagged)
    cv2.circle(mask, (cx_s, cy_s), max(1, r_s), 255, -1)

def is_pixel_flagged(mask, pos):
    """
    Checks if a point (cx, cy) is already flagged.
    """
    cx, cy = pos
    cx_s = int(cx / MASK_SCALE)
    cy_s = int(cy / MASK_SCALE)
    
    if 0 <= cy_s < mask.shape[0] and 0 <= cx_s < mask.shape[1]:
        return mask[cy_s, cx_s] > 0
    return False
