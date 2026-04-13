import matplotlib.pyplot as plt
import numpy as np
import os

def plot_density_map(craters, img_shape, title="Crater Density Map"):
    """
    Generates a heatmap showing the spatial concentration of craters (Section 2.7.1).
    """
    if not craters:
        print("No craters to plot density map.")
        return
        
    h, w = img_shape
    # Create a 2D histogram
    # Using a grid size that makes sense for the image resolution
    grid_size = 50 
    heatmap, xedges, yedges = np.histogram2d(
        [c[1] for c in craters], # y
        [c[0] for c in craters], # x
        bins=[h // grid_size, w // grid_size],
        range=[[0, h], [0, w]]
    )
    
    plt.figure(figsize=(10, 8))
    plt.imshow(heatmap, extent=[0, w, h, 0], cmap='hot', interpolation='gaussian')
    plt.colorbar(label='Crater Count per Grid Cell')
    plt.title(title)
    plt.xlabel("X (pixels)")
    plt.ylabel("Y (pixels)")
    
    os.makedirs("outputs/plots", exist_ok=True)
    save_path = "outputs/plots/density_map.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Density map saved to {save_path}")
