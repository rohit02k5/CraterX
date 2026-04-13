import matplotlib.pyplot as plt
import numpy as np
import os

def plot_enhanced_csfd(diams_meters, area_km2, save_path):
    """
    Plots a scientifically valid CSFD (Cumulative Size-Frequency Distribution).
    Exports .diam file for Craterstats analysis.
    """
    if len(diams_meters) == 0:
        print("[WARN] No craters to plot CSFD.")
        return

    # Export .diam file (Standard planetary science format)
    diam_file = save_path.replace(".png", ".diam")
    # Sort descending for .diam conventionally or just standard list
    with open(diam_file, "w") as f:
        f.write("# Diameter (m)\n")
        f.write(f"# Area (km2): {area_km2:.6f}\n")
        for d in sorted(diams_meters, reverse=True):
            f.write(f"{d:.4f}\n")
    print(f"[INFO] Exported .diam file to {diam_file}")

    # Calculate cumulative statistics
    unique_diams = np.sort(np.unique(diams_meters))
    counts = []
    errors = []
    
    for d in unique_diams:
        N = np.sum(diams_meters >= d)
        # N(D) per km2
        counts.append(N / area_km2)
        # Poisson Error: sqrt(N) / Area
        errors.append(np.sqrt(N) / area_km2)

    # Visualization
    plt.figure(figsize=(8, 6))
    plt.errorbar(unique_diams, counts, yerr=errors, fmt='o', color='red', ecolor='gray', 
                 capsize=2, label='Detections (m)')
    
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Diameter D (m)')
    plt.ylabel('Cumulative Frequency N(D) (km$^{-2}$)')
    plt.title('Crater Size-Frequency Distribution')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()
