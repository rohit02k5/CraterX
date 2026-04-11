import matplotlib.pyplot as plt

import numpy as np

def plot_csfd(diams, area_km2=1.0):
    if not diams:
        print("No craters to plot.")
        return
        
    diams = np.sort(np.array(diams))
    n = len(diams)
    
    # Cumulative counts: for each diameter, how many craters are >= to it
    counts = np.arange(n, 0, -1) / area_km2
    
    plt.figure(figsize=(8, 6))
    plt.loglog(diams, counts, 'b-', label='Detected')
    plt.xlabel("Diameter (m)")
    plt.ylabel("Cumulative Frequency (N > D per km²)")
    plt.title("Crater Size-Frequency Distribution (CSFD)")
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend()
    
    # Ensure directory exists
    import os
    os.makedirs("outputs/plots", exist_ok=True)
    plt.savefig("outputs/plots/csfd_plot.png")
    plt.close()
