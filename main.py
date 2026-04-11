from src.preprocess import load_images
from src.detection import detect_lowlights, find_highlight
from src.guide_params import compute_guide_params
from src.fitting import fit_crater
from src.templates import build_templates, refine_with_templates
from src.matching import match_craters
import numpy as np
import cv2

import glob
import os

RAW_DIR = "data/raw"
IMAGE_PATHS = glob.glob(os.path.join(RAW_DIR, "*.tif"))

if not IMAGE_PATHS:
    print(f"No .tif images found in {RAW_DIR}. Please add them to proceed.")
    exit()

print(f"Found {len(IMAGE_PATHS)} images: {IMAGE_PATHS}")

images = load_images(IMAGE_PATHS)

all_craters = []

for i, img in enumerate(images):
    # If image is too large, process only a crop for testing or use strips
    # For now, let's sample a 2000x2000 region to avoid memory issues with 500MB+ TIF
    if img.shape[0] > 2000 or img.shape[1] > 2000:
        print(f"Image {i+1} is large ({img.shape}), cropping to 2000x2000 for analysis.")
        img = img[5000:7000, 5000:7000] # Random crop in the middle-ish
        # Local normalization for the crop
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        images[i] = img
        
    lowlights = detect_lowlights(img)
    print(f"Image {i+1}: Found {len(lowlights)} shadow candidates.")
    
    if not lowlights:
        all_craters.append([])
        continue

    guide_dir, guide_dist = compute_guide_params(img, lowlights)
    
    craters = []

    for low in lowlights:
        high = find_highlight(img, low, guide_dir, guide_dist)
        if high is None:
            continue

        crater = fit_crater(img, low, high)
        if crater:
            craters.append(crater)

    all_craters.append(craters)
    print(f"Image {i+1} ({os.path.basename(IMAGE_PATHS[i])}): Detected {len(craters)} candidates.")

# Cross-view matching
if len(all_craters) > 1:
    print("Performing multi-image matching...")
    final_craters = match_craters(all_craters)
    if len(final_craters) == 0:
        print("Warning: No matching craters found across images. Falling back to union of all detections.")
        # Fallback to union
        union_set = []
        for img_craters in all_craters:
            union_set.extend(img_craters)
        final_craters = union_set
else:
    final_craters = all_craters[0]

print("Final crater count:", len(final_craters))

# Draw results and save overlays
import os
import cv2
os.makedirs("outputs/overlays", exist_ok=True)

for i, img in enumerate(images):
    overlay = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for cx, cy, d in final_craters:
        cv2.circle(overlay, (int(cx), int(cy)), int(d/2), (0, 255, 0), 2)
    
    cv2.imwrite(f"outputs/overlays/img{i+1}_overlay.png", overlay)

# Save result list to CSV
import csv
os.makedirs("outputs/crater_lists", exist_ok=True)
csv_path = "outputs/crater_lists/detected_craters.csv"
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['x', 'y', 'diameter'])
    for crater in final_craters:
        writer.writerow(crater)
print(f"Saved {len(final_craters)} craters to {csv_path}")

# Plot CSFD
from src.csfd import plot_csfd
diams = [c[2] for c in final_craters]
plot_csfd(diams)
