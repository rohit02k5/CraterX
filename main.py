from src.preprocess import load_images
from src.detection import detect_lowlights, find_highlight
from src.guide_params import compute_guide_params
from src.fitting import fit_crater
from src.templates import build_class_templates, refine_with_freshness_templates
from src.matching import match_craters_multi_view
from src.csfd import plot_enhanced_csfd
from src.visualization import plot_density_map
import numpy as np
import cv2
import glob
import os
import csv

RAW_DIR = "data/raw"
IMAGE_PATHS = glob.glob(os.path.join(RAW_DIR, "*.tif"))

if not IMAGE_PATHS:
    print(f"No .tif images found in {RAW_DIR}. Please add them to proceed.")
    exit()

print(f"Found {len(IMAGE_PATHS)} images: {IMAGE_PATHS}")

images = load_images(IMAGE_PATHS)
all_craters_by_img = []

for i, img in enumerate(images):
    # Process crop if large
    if img.shape[0] > 1000 or img.shape[1] > 1000:
        print(f"Image {i+1} is large, cropping to 1000x1000 for faster demonstration.")
        img = img[5000:6000, 5000:6000]
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        images[i] = img
        
    # 1. Detection with Contrast Limit
    lowlights = detect_lowlights(img, contrast_limit=47)
    print(f"Image {i+1}: Found {len(lowlights)} candidate shadows after contrast filter.")
    
    if not lowlights:
        all_craters_by_img.append([])
        continue

    # 2. Guide Parameters for Sun Angle
    guide_dir, guide_dist = compute_guide_params(img, lowlights)
    
    initial_craters = []
    for low in lowlights:
        high = find_highlight(img, low, guide_dir, guide_dist)
        if high is None: continue

        # 3. Iterative Sub-pixel Fitting
        crater = fit_crater(img, low, high)
        if crater:
            initial_craters.append(crater)

    all_craters_by_img.append(initial_craters)
    print(f"Image {i+1}: Detected {len(initial_craters)} initial craters.")

# 4. Multi-Image Matching with Registration Correction
print("Performing robust multi-image matching (XY Discrepancy)...")
final_craters = match_craters_multi_view(all_craters_by_img)
print(f"Certified {len(final_craters)} craters found across multiple views.")

# 5. Template Refinement & Freshness Classification
# Extract all craters across images to build template library
union_set = []
for img_craters in all_craters_by_img:
    union_set.extend(img_craters)

if final_craters:
    print("Building class-specific templates and refining...")
    class_templates = build_class_templates(union_set, images[0])
    refined_craters = refine_with_freshness_templates(final_craters, class_templates, images[0])
else:
    refined_craters = []

print("Final certified crater count:", len(refined_craters))

# 6. Save Results & Visualizations
os.makedirs("outputs/overlays", exist_ok=True)
os.makedirs("outputs/crater_lists", exist_ok=True)

# Overlay
for i, img in enumerate(images):
    overlay = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for c in refined_craters:
        cx, cy, d, freshness = c
        # Color by freshness?
        color = (0, 255, 0) # Default green
        if freshness == "Prominent": color = (0, 0, 255) # Red
        elif freshness == "Vague": color = (200, 200, 200) # Gray
        
        cv2.circle(overlay, (int(cx), int(cy)), int(d/2), color, 2)
        cv2.putText(overlay, freshness[0], (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    cv2.imwrite(f"outputs/overlays/img{i+1}_final_overlay.png", overlay)

# CSV with Freshness
csv_path = "outputs/crater_lists/detected_craters.csv"
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['x', 'y', 'diameter', 'freshness'])
    for crater in refined_craters:
        writer.writerow(crater)

# Enhanced CSFD
diams = [c[2] for c in refined_craters]
plot_enhanced_csfd(diams)

# Density Map
plot_density_map(refined_craters, images[0].shape)

print("Process complete. All research paper results (CSFD, Density Maps, Freshness) generated.")
