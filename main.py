import os
import glob
import cv2
import numpy as np
from src.preprocess import load_image_metadata, get_thumbnail, load_single_image, split_into_strips
from src.guide_params import compute_guide_params
from src.detection import detect_lowlights, find_highlight
from src.fitting import fit_crater
from src.pixel_flagging import flag_pixels
from src.matching import match_craters_multi_view_optimized
from src.templates import build_class_templates, refine_with_freshness_templates
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
    
    all_view_craters = []
    
    # 1. Processing candidates one-by-one to save memory
    from src.pixel_flagging import MASK_SCALE, is_pixel_flagged
    
    for i, path in enumerate(image_paths):
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
            guide_dir, guide_dist = compute_guide_params(strip_data, candidates)
            if guide_dir is None: continue

            for low in candidates:
                high_pt = find_highlight(strip_data, low, guide_dir, guide_dist)
                if high_pt:
                    res = fit_crater(strip_data, low, high_pt)
                    if res:
                        cx, cy, d_m, _ = res
                        cx_g, cy_g = cx + x_off, cy + y_off
                        
                        if not is_pixel_flagged(used_mask, (cx_g, cy_g)):
                            view_craters.append((cx_g, cy_g, d_m, "Vague", i))
                            flag_pixels(used_mask, (cx_g, cy_g, d_m / (2 * PIXEL_SIZE_METERS)))
                            
        all_view_craters.append(view_craters)
        print(f"  Found {len(view_craters)} candidates.", flush=True)
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
    roi_craters = [c for c in final_catalog if is_in_roi(c, (ROI_CENTER_X, ROI_CENTER_Y), ROI_RADIUS_METERS, PIXEL_SIZE_METERS)]
    
    os.makedirs("outputs/crater_lists", exist_ok=True)
    with open("outputs/crater_lists/research_catalog.csv", "w") as f:
        f.write("x_px,y_px,diameter_m,freshness\n")
        for c in roi_craters:
            f.write(f"{c[0]:.2f},{c[1]:.2f},{c[2]:.2f},{c[3]}\n")

    area_km2 = calculate_roi_area_km2(ROI_RADIUS_METERS)
    plot_enhanced_csfd([c[2] for c in roi_craters], area_km2, "outputs/plots/csfd_plot_research.png")
    plot_density_map(roi_craters, ref_img.shape, PIXEL_SIZE_METERS, "outputs/plots/density_heatmap.png", 
                    roi=(ROI_CENTER_X, ROI_CENTER_Y, ROI_RADIUS_METERS))

    # ROI Overlay
    overlay = cv2.normalize(ref_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    overlay = cv2.cvtColor(overlay, cv2.COLOR_GRAY2BGR)
    cv2.circle(overlay, (ROI_CENTER_X, ROI_CENTER_Y), int(ROI_RADIUS_METERS/PIXEL_SIZE_METERS), (0, 0, 255), 3)
    for c in roi_craters:
        cx, cy, d_m, f = c
        d_px = d_m / PIXEL_SIZE_METERS
        cv2.circle(overlay, (int(cx), int(cy)), int(d_px/2), (0, 255, 0), 1)
        cv2.putText(overlay, f[0], (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imwrite("outputs/overlays/research_final_overlay.png", overlay)
    print("\nProcessing Complete.", flush=True)

if __name__ == "__main__":
    main()
