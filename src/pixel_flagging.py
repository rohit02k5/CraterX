import numpy as np

def flag_pixels(mask, crater):
    # mask is a boolean array
    cx, cy, d = crater
    h, w = mask.shape
    r = d/2
    
    y, x = np.ogrid[:h, :w]
    crater_mask = (x-cx)**2 + (y-cy)**2 < r**2
    mask[crater_mask] = True
