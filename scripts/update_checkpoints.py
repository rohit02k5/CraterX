import os
import glob
import json
import cv2
import sys

# Ensure parent dir is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocess import load_single_image
from src.templates import extract_patch, classify_freshness
from config import IMAGE_METADATA

def update_checkpoints():
    checkpoints = glob.glob("outputs/checkpoints/*_candidates.json")
    if not checkpoints:
        print("No checkpoints found.")
        return

    for ckpt in checkpoints:
        img_id = os.path.basename(ckpt).split('_candidates')[0]
        raw_path = f"data/raw/{img_id}.tif"
        
        if not os.path.exists(raw_path):
            print(f"Skipping {ckpt}, no raw image found.")
            continue
            
        print(f"Updating checkpoint for {img_id}...")
        img = load_single_image(raw_path)
        scale = IMAGE_METADATA.get(img_id, {"scale": 0.5})["scale"]
        
        with open(ckpt, "r") as f:
            craters = json.load(f)
            
        updated_craters = []
        for c in craters:
            cx, cy, d_m, freshness, img_idx = c
            d_px = d_m / scale
            
            # cx, cy in JSON are global coordinates! So we can directly extract patch from full image
            patch = extract_patch(img, cx, cy, d_px)
            new_freshness = classify_freshness(patch, d_px)
            
            updated_craters.append([cx, cy, d_m, new_freshness, img_idx])
            
        with open(ckpt, "w") as f:
            json.dump(updated_craters, f)
            
    print("All checkpoints successfully updated!")

if __name__ == "__main__":
    update_checkpoints()
