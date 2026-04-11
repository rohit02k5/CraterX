import cv2
import os

raw_dir = "data/raw"
for f in os.listdir(raw_dir):
    if f.endswith(".tif"):
        path = os.path.join(raw_dir, f)
        # Use cv2.imread with IMREAD_UNCHANGED to get proper shape without loading full data if possible
        # Actually cv2.imread loads the whole thing. For shape only, we can use PIL
        try:
            from PIL import Image
            Image.MAX_IMAGE_PIXELS = None
            with Image.open(path) as img:
                print(f"{f}: {img.size} (Width, Height)")
        except ImportError:
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                print(f"{f}: {img.shape} (Height, Width)")
            else:
                print(f"{f}: Failed to load")
