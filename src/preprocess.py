import cv2
import numpy as np
import tifffile
try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

def load_image_metadata(paths):
    """
    Extracts metadata from large GeoTIFFs without loading the full pixel array.
    """
    metadata = []
    for p in paths:
        meta = {"path": p, "pixel_scale": 0.5}
        if HAS_RASTERIO:
            with rasterio.open(p) as src:
                meta["transform"] = src.transform
                meta["crs"] = src.crs
                meta["pixel_scale"] = src.res[0]
                meta["shape"] = src.shape
        else:
            # Fallback using tifffile metadata
            with tifffile.TiffFile(p) as tif:
                meta["shape"] = tif.pages[0].shape
        metadata.append(meta)
    return metadata

def get_thumbnail(path, scale=0.1):
    """
    Loads a downsampled version of a large image for registration.
    """
    img = tifffile.imread(path)
    h, w = img.shape
    small = cv2.resize(img, (int(w*scale), int(h*scale)))
    return small.astype(np.float32)

def load_single_image(path):
    """
    Loads one image into float32.
    """
    img = tifffile.imread(path)
    return img.astype(np.float32)


def split_into_strips(img, strip_size=(2000, 2000), overlap=200):
    """
    Splits image into overlapping strips to ensure craters on boundaries are caught.
    Returns list of (strip_data, y_offset, x_offset).
    """
    h, w = img.shape
    sh, sw = strip_size
    strips = []
    
    y_step = sh - overlap
    x_step = sw - overlap
    
    for y in range(0, h, y_step):
        for x in range(0, w, x_step):
            y_end = min(y + sh, h)
            x_end = min(x + sw, w)
            
            strip = img[y:y_end, x:x_end]
            strips.append((strip, y, x))
            
            if x_end == w: break
        if y_end == h: break
        
    return strips
