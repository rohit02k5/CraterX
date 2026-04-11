import cv2
import numpy as np
import os

def create_synthetic_crater(img, cx, cy, radius, sun_angle_deg=45):
    """
    Draws a synthetic crater with shadow and highlight.
    """
    # Shadow (lowlight)
    angle_rad = np.deg2rad(sun_angle_deg)
    shadow_offset_x = -int(radius * 0.4 * np.cos(angle_rad))
    shadow_offset_y = -int(radius * 0.4 * np.sin(angle_rad))
    
    cv2.circle(img, (cx + shadow_offset_x, cy + shadow_offset_y), int(radius * 0.8), (20, 20, 20), -1)
    
    # Highlight
    highlight_offset_x = -shadow_offset_x
    highlight_offset_y = -shadow_offset_y
    cv2.circle(img, (cx + highlight_offset_x, cy + highlight_offset_y), int(radius * 0.5), (200, 200, 200), -1)
    
    # Crater rim (subtle)
    cv2.circle(img, (cx, cy), radius, (100, 100, 100), 1)

def main():
    os.makedirs("data", exist_ok=True)
    img_size = 1000
    
    # Fix crater locations for all images
    num_craters = 10
    crater_locations = []
    for _ in range(num_craters):
        cx = np.random.randint(100, img_size - 100)
        cy = np.random.randint(100, img_size - 100)
        radius = np.random.randint(15, 40)
        crater_locations.append((cx, cy, radius))

    for i in range(1, 5):
        # Background: noisy gray, slightly different for each image
        img = np.random.normal(128, 15, (img_size, img_size)).astype(np.uint8)
        
        # Add the same craters
        for cx, cy, radius in crater_locations:
            # Vary sun angle slightly
            sun_angle = 45 + np.random.randint(-5, 5)
            create_synthetic_crater(img, cx, cy, radius, sun_angle)
            
        filename = f"data/img{i}.tif"
        cv2.imwrite(filename, img)
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()
