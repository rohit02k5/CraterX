import matplotlib.pyplot as plt

import numpy as np

import matplotlib.pyplot as plt
import numpy as np
import os

def plot_enhanced_csfd(diams, area_km2=1.0, title="Crater Size-Frequency Distribution (CSFD)"):
    """
    Plots the CSFD with sqrt(N) error bars as standard in lunar science.
    """
    if not diams:
        print("No craters to plot.")
        return
        
    diams = np.sort(np.array(diams))
    n = len(diams)
    
    # Cumulative counts: N > D
    # We plot it from largest to smallest to get the cumulative effect properly
    unique_diams = np.unique(diams)
    cumulative_counts = []
    for d in unique_diams:
        count = np.sum(diams >= d)
        cumulative_counts.append(count)
    
    cumulative_counts = np.array(cumulative_counts)
    y = cumulative_counts / area_km2
    x = unique_diams
    
    # Poisson error: sqrt(N)
    y_err = (np.sqrt(cumulative_counts) / area_km2)
    
    plt.figure(figsize=(10, 8))
    plt.errorbar(x, y, yerr=y_err, fmt='bo', markersize=3, capsize=2, label='Detected Craters', alpha=0.7)
    plt.loglog(x, y, 'b-')
    
    plt.xlabel("Diameter D (m)", fontsize=12)
    plt.ylabel("Cumulative Frequency N(D) per km²", fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.legend()
    
    os.makedirs("outputs/plots", exist_ok=True)
    save_path = "outputs/plots/csfd_plot_enhanced.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Enhanced CSFD plot saved to {save_path}")
