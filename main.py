import os
import glob
import cv2
import json
import numpy as np
from src.preprocess import load_image_metadata, get_thumbnail, load_single_image, split_into_strips
from src.guide_params import compute_guide_params
from src.detection import detect_lowlights, find_highlight
from src.fitting import fit_crater
from src.pixel_flagging import flag_pixels
from src.matching import match_craters_multi_view_optimized
from src.templates import build_class_templates, refine_with_freshness_templates, extract_patch, classify_freshness
from src.csfd import plot_enhanced_csfd
from src.visualization import plot_density_map
from src.roi import calculate_roi_area_km2, is_in_roi
from config import *

def main():
    print("Starting Memory-Efficient Research-Grade Pipeline...", flush=True)
    
    image_paths = sorted(glob.glob("data/raw/*.tif"))
    if not image_paths:
        print("No .tif images found in data/raw/", flush=True)
        return
    
    metadata = load_image_metadata(image_paths)
    print(f"Total Images: {len(metadata)}", flush=True)
    
    os.makedirs("outputs/checkpoints", exist_ok=True)
    all_view_craters = []
    
    # 1. Processing candidates one-by-one to save memory
    from src.pixel_flagging import MASK_SCALE, is_pixel_flagged
    
    for i, path in enumerate(image_paths):
        img_id = os.path.basename(path).split('.')[0]
        checkpoint_path = f"outputs/checkpoints/{img_id}_candidates.json"
        
        # RESUME LOGIC: Check if we already processed this image
        if os.path.exists(checkpoint_path):
            print(f"\n[1/4] Loading cached candidates for {img_id}...", flush=True)
            with open(checkpoint_path, "r") as f:
                view_craters = json.load(f)
            all_view_craters.append(view_craters)
            continue

        print(f"\n[1/4] Processing image {i+1}/{len(image_paths)}: {os.path.basename(path)}", flush=True)
        img = load_single_image(path)
        
        # Optimized uint8 mask at 4x downsampling
        mask_h = int(img.shape[0] / MASK_SCALE) + 1
        mask_w = int(img.shape[1] / MASK_SCALE) + 1
        used_mask = np.zeros((mask_h, mask_w), dtype=np.uint8)
        
        view_craters = []
        strips = split_into_strips(img, strip_size=STRIP_SIZE, overlap=STRIP_OVERLAP)
        print(f"Divided into {len(strips)} strips.", flush=True)
        
        for s_idx, (strip_data, y_off, x_off) in enumerate(strips):
            if s_idx % 5 == 0:
                print(f"  Strip {s_idx}/{len(strips)}...", flush=True)
                
            candidates = detect_lowlights(strip_data, shadow_percentile=SHADOW_PERCENTILE, min_diameter=MIN_DIAMETER_PIXELS)
            guide_dir, guide_dist = compute_guide_params(strip_data, candidates, img_path=path)
            if guide_dir is None: continue

            for low in candidates:
                high_pt = find_highlight(strip_data, low, guide_dir, guide_dist)
                if high_pt:
                    # Use image-specific scale for 100% accurate meters
                    scale = IMAGE_METADATA.get(img_id, {"scale": 0.5})["scale"]
                    res = fit_crater(strip_data, low, high_pt, pixel_scale=scale)
                    if res:
                        cx, cy, d_m, _ = res
                        cx_g, cy_g = cx + x_off, cy + y_off
                        
                        if not is_pixel_flagged(used_mask, (cx_g, cy_g)):
                            # Format suitable for JSON: [cx, cy, d_m, freshness, img_idx]
                            d_px = d_m / scale
                            patch = extract_patch(strip_data, cx, cy, d_px)
                            freshness = classify_freshness(patch, d_px)
                            view_craters.append([float(cx_g), float(cy_g), float(d_m), freshness, i])
                            flag_pixels(used_mask, (cx_g, cy_g, d_m / (2 * PIXEL_SIZE_METERS)))
                            
        # Save checkpoint immediately
        with open(checkpoint_path, "w") as f:
            json.dump(view_craters, f)
            
        all_view_craters.append(view_craters)
        print(f"  Found {len(view_craters)} candidates. Saved to cache.", flush=True)
        del img, used_mask
        import gc; gc.collect()

    # 2. Certification using thumbnails
    print("\n[2/4] Performing Multi-View Certification...", flush=True)
    thumbnails = [get_thumbnail(p, scale=0.05) for p in image_paths]
    certified_craters = match_craters_multi_view_optimized(all_view_craters, thumbnails)
    print(f"Certified {len(certified_craters)} craters.", flush=True)

    if not certified_craters:
        print("No craters survived certification.", flush=True)
        return

    # 3. Refinement
    print("\n[3/4] Refining with freshness templates...", flush=True)
    ref_img = load_single_image(image_paths[0])
    templates = build_class_templates(certified_craters, [ref_img] * len(image_paths))
    final_catalog = refine_with_freshness_templates(certified_craters, [ref_img] * len(image_paths), templates)

    # 4. Science Filtering & Visualization
    print("\n[4/4] Generating outputs...", flush=True)
    
    os.makedirs("outputs/crater_lists", exist_ok=True)
    from src.utils import pixel_to_latlon
    transform = metadata[0].get('transform', None)

    # ================= FULL MAP OUTPUTS =================
    full_craters = final_catalog
    with open("outputs/crater_lists/research_catalog_FULL.csv", "w") as f:
        f.write("x_px,y_px,lat,lon,diameter_m,freshness\n")
        for c in full_craters:
            lat, lon = pixel_to_latlon(c[0], c[1], transform)
            f.write(f"{c[0]:.2f},{c[1]:.2f},{lat:.6f},{lon:.6f},{c[2]:.2f},{c[3]}\n")

    area_km2_full = (ref_img.shape[0] * PIXEL_SIZE_METERS / 1000) * (ref_img.shape[1] * PIXEL_SIZE_METERS / 1000)
    plot_enhanced_csfd([c[2] for c in full_craters], area_km2_full, "outputs/plots/csfd_plot_FULL.png")
    plot_density_map(full_craters, ref_img.shape, PIXEL_SIZE_METERS, "outputs/plots/density_heatmap_FULL.png", roi=None)

    overlay_full = cv2.normalize(ref_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    overlay_full = cv2.cvtColor(overlay_full, cv2.COLOR_GRAY2BGR)
    for c in full_craters:
        cx, cy, d_m, f = c
        d_px = max(2, d_m / PIXEL_SIZE_METERS)
        # High-tech HUD visualization
        # Inner exact crater size (Thin Bright Green)
        cv2.circle(overlay_full, (int(cx), int(cy)), int(d_px/2), (0, 255, 0), 1)
        # Outer target ring (Thick Cyan)
        cv2.circle(overlay_full, (int(cx), int(cy)), int(d_px/2) + 10, (255, 255, 0), 2)
    cv2.imwrite("outputs/overlays/research_overlay_FULL.png", overlay_full)

    # ================= ROI ONLY OUTPUTS =================
    roi_craters = [c for c in final_catalog if is_in_roi(c, (ROI_CENTER_X, ROI_CENTER_Y), ROI_RADIUS_METERS, PIXEL_SIZE_METERS)]
    with open("outputs/crater_lists/research_catalog_ROI.csv", "w") as f:
        f.write("x_px,y_px,lat,lon,diameter_m,freshness\n")
        for c in roi_craters:
            lat, lon = pixel_to_latlon(c[0], c[1], transform)
            f.write(f"{c[0]:.2f},{c[1]:.2f},{lat:.6f},{lon:.6f},{c[2]:.2f},{c[3]}\n")

    area_km2_roi = calculate_roi_area_km2(ROI_RADIUS_METERS)
    plot_enhanced_csfd([c[2] for c in roi_craters], area_km2_roi, "outputs/plots/csfd_plot_ROI.png")
    plot_density_map(roi_craters, ref_img.shape, PIXEL_SIZE_METERS, "outputs/plots/density_heatmap_ROI.png", roi=(ROI_CENTER_X, ROI_CENTER_Y, ROI_RADIUS_METERS))

    overlay_roi = cv2.normalize(ref_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    overlay_roi = cv2.cvtColor(overlay_roi, cv2.COLOR_GRAY2BGR)
    cv2.circle(overlay_roi, (ROI_CENTER_X, ROI_CENTER_Y), int(ROI_RADIUS_METERS/PIXEL_SIZE_METERS), (0, 0, 255), 3)
    for c in roi_craters:
        cx, cy, d_m, f = c
        d_px = max(2, d_m / PIXEL_SIZE_METERS)
        # High-tech HUD visualization
        cv2.circle(overlay_roi, (int(cx), int(cy)), int(d_px/2), (0, 255, 0), 1)
        cv2.circle(overlay_roi, (int(cx), int(cy)), int(d_px/2) + 10, (255, 255, 0), 2)
        # HUD Text Label
        cv2.putText(overlay_roi, f[0], (int(cx) + 12, int(cy) + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    cv2.imwrite("outputs/overlays/research_overlay_ROI.png", overlay_roi)

    print("\nProcessing Complete.", flush=True)

if __name__ == "__main__":
    main()
