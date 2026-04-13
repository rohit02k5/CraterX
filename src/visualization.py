import matplotlib.pyplot as plt
import numpy as np
import cv2

def plot_density_map(craters, img_shape, pixel_scale, save_path, roi=None):
    """
    Generates a spatial density heatmap in km coordinates.
    Includes ROI overlay.
    """
    h, w = img_shape
    # Scale grid size to image resolution
    grid_res = max(50, int(max(h, w) / 100))
    
    # Convert crater pixels to kilometers
    cx = [c[0] * pixel_scale / 1000.0 for c in craters]
    cy = [c[1] * pixel_scale / 1000.0 for c in craters]
    
    plt.figure(figsize=(10, 8))
    # 2D Histogram for density
    counts, xedges, yedges, im = plt.hist2d(cx, cy, bins=grid_res, cmap='viridis', density=False)
    plt.colorbar(label='Crater Density (Count per cell)')
    
    # ROI Overlay (Section 2.7.1)
    if roi:
        roi_cx, roi_cy, roi_r_m = roi
        roi_cx_km = roi_cx * pixel_scale / 1000.0
        roi_cy_km = roi_cy * pixel_scale / 1000.0
        roi_r_km = roi_r_m / 1000.0
        
        circle = plt.Circle((roi_cx_km, roi_cy_km), roi_r_km, color='red', fill=False, 
                            linewidth=2, label='ROI (Landing Zone)')
        plt.gca().add_patch(circle)
        plt.legend()

    plt.xlabel('Distance East (km)')
    plt.ylabel('Distance North (km)')
    plt.title('Spatial Crater Density Map')
    plt.gca().invert_yaxis()
    plt.savefig(save_path)
    plt.close()
