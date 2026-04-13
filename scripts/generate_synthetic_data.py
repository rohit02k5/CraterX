import numpy as np
import cv2
import os
import tifffile

def create_realistic_crater(img, cx, cy, d, contrast=2000):
    """
    Creates a crater with a smooth radial brightness gradient (photometrically realistic).
    """
    r = d / 2
    h, w = img.shape
    y, x = np.ogrid[:h, :w]
    dist_sq = (x - cx)**2 + (y - cy)**2
    mask = dist_sq <= r**2
    
    # Shadow (dark half)
    shadow_mask = mask & (x < cx)
    img[shadow_mask] -= contrast * np.cos(np.pi * np.sqrt(dist_sq[shadow_mask]) / (2*r))
    
    # Highlight (bright half)
    highlight_mask = mask & (x >= cx)
    img[highlight_mask] += contrast * np.cos(np.pi * np.sqrt(dist_sq[highlight_mask]) / (2*r))
    
    return img

def main():
    os.makedirs("data/raw", exist_ok=True)
    img_size = 2000 # Larger for strip testing
    
    # Create 4 images with slight offsets and different sun angles (approximated)
    for i in range(4):
        # Base terrain with noise
        img = np.full((img_size, img_size), 32768, dtype=np.uint16)
        img = img + np.random.normal(0, 500, (img_size, img_size)).astype(np.int32)
        img = np.clip(img, 0, 65535).astype(np.uint16)
        
        # Add craters in consistent locations (with slight registration shift)
        shift_x, shift_y = i * 2, i * 1
        
        # 1. Large Crater (Testing multiscale/rejection)
        create_realistic_crater(img, 500+shift_x, 500+shift_y, 100, contrast=5000)
        
        # 2. Small Fresh Craters
        create_realistic_crater(img, 200+shift_x, 800+shift_y, 20, contrast=8000)
        create_realistic_crater(img, 1200+shift_x, 400+shift_y, 15, contrast=9000)
        
        # 3. Many Tiny Craters (3-5 pixels)
        for j in range(20):
            tx = np.random.randint(100, 1900)
            ty = np.random.randint(100, 1900)
            td = np.random.randint(3, 8)
            create_realistic_crater(img, tx, ty, td, contrast=4000)
            
        out_path = f"data/raw/synthetic_{i}.tif"
        tifffile.imwrite(out_path, img)
        print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
