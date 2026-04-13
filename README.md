# 🌔 Lunar Crater Detection System

A research-grade computer vision pipeline designed for high-precision crater counting and analysis on high-resolution LROC NAC imagery (0.5m/pixel). This system is optimized for scientific validity (multi-view certification) and large-scale memory efficiency.

---

## 💻 Setup Instructions (New Laptop)

Follow these steps to set up the environment and run the pipeline:

### 1. Prerequisites
Ensure you have **Python 3.9+** installed. This project requires significant RAM for processing 720-megapixel images (16GB+ recommended).

### 2. Install Dependencies
Run the following commands to install the required scientific and image processing libraries:

```bash
pip install numpy opencv-python matplotlib tifffile imagecodecs rasterio scipy
```

> [!NOTE]
> `imagecodecs` and `tifffile` are essential for handling 16-bit LROC NAC depth without photometric loss. `rasterio` is used for GeoTIFF metadata extraction.

### 3. Folder Preparation
Ensure the following directory structure exists in your project root:
```text
crater_project/
├── data/
│   ├── raw/             <-- Place your .tif images here
│   └── processed/
├── outputs/
│   ├── crater_lists/    <-- Results (CSV, .diam) will be here
│   ├── plots/           <-- CSFD and Density maps
│   └── overlays/        <-- Visual confirmation images
└── src/                 <-- All source modules
```

### 4. Configuration
Edit `config.py` to match your specific landing site parameters:
- `PIXEL_SIZE_METERS`: Set to `0.5` for LROC NAC.
- `ROI_RADIUS_METERS`: Radius of the analysis area (e.g., `500` for 500m Landing Zone).
- `MIN_VIEWS_FOR_CERT`: Set to `2` for scientific certification.

### 5. Running the Pipeline
Place your target `.tif` images in `data/raw/` and execute:
```bash
python main.py
```

---

## 🔬 Scientific Methodology

This implementation aligns with the **Ganesh et al. (2022)** research-grade standard:
1.  **16-bit Preservation**: Full dynamic range (0-65535 DN) is used for shadow detection.
2.  **Overlapping Strips**: 2000px strips with 200px overlap solve for boundary artifacts.
3.  **Adaptive Thresholding**: Global thresholds are replaced with local 15th-percentile shadow detection per strip.
4.  **Multi-View Certification**: Craters are only recorded if confirmed in $\ge 2$ independent images.
5.  **Sub-pixel Accuracy**: Centers and diameters are refined via iterative contrast maximization.

## 📊 Outputs
- **`research_catalog.csv`**: Full list of certified craters (X, Y, Diameter (m), Freshness).
- **`csfd_plot_research.png`**: Scientific plot with Poisson error bars.
- **`research_final_overlay.png`**: High-resolution image with all detections drawn.
- **`.diam` Export**: Standard format compatible with **Craterstats 2.0**.

---
*Developed for the DIP Lunar Landing Safety Project.*
