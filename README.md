# 🌔 Lunar Crater Detection System (RegolithMapper)

A research-grade, memory-efficient computer vision pipeline for detecting and measuring lunar craters in high-resolution LROC NAC imagery. This system is mathematically aligned with the methodology of **Ganesh et al. (2022)**.

---

## 🚀 Deployment Overview
This pipeline is designed for long-running, mission-critical scientific analysis. It is optimized for high-end workstations and features a robust "Quick Resume" system to protect against hardware restarts or crashes.

### 🧪 Key Scientific Features
- **16-Bit Photometric Integrity**: Preserves full LROC NAC dynamic range (0–65535 DN) using `tifffile` and `rasterio`.
- **Multi-View Certification**: Uses a **UNION-set matching engine** to cross-reference detections across multiple orbital views, eliminating false positives and noise.
- **Sub-Pixel Diameter Solver**: Employs an iterative contrast-maximization algorithm to achieve **0.5-pixel precision**.
- **Geospatial Support**: Automatically converts X/Y pixel coordinates to **Latitude and Longitude** using GeoTIFF affine transforms.
- **CSFD & chronology**: Generates Cumulative Size-Frequency Distribution plots and exports `.diam` files compatible with **Craterstats**.

---

## 💻 System Setup

### 1. Requirements
Ensure your machine has **Python 3.9+** and a dedicated GPU (for general system performance, as the code is CPU-multithreaded and vector-optimized for massive datasets).

```bash
# Clone the repository
git clone <repository-url>
cd crater_project

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Preparation
Place your raw **16-bit GeoTIFF** LROC NAC images in the `data/raw/` directory.
- The system expects `.tif` or `.tiff` files.
- Each image must have internal GeoTIFF metadata if you want Lat/Lon output.

---

## ⚙️ Configuration (`config.py`)
Before running, tune the following constants to your target landing site:

| Constant | Default | Description |
|----------|---------|-------------|
| `PIXEL_SIZE_METERS` | 0.5 | Native scale of LROC NAC. |
| `ROI_RADIUS_METERS` | 500 | Radius of the search area around the landing site. |
| `IMAGE_METADATA` | - | **CRITICAL**: Add your image IDs and sun angles here to skip 8+ hours of solar estimation. |

---

## 🏃 Running the Pipeline
Run the main script from the root directory:
```bash
python main.py
```

### 🛡️ Crash Protection (Checkpointing)
Detections take approximately **12–20 hours** for a full-resolution 4-image cohort.
- **Auto-Save**: The system saves candidates in `outputs/checkpoints/` after each image finishes.
- **Resuming**: If the script stops, simply run `python main.py` again. It will detect the cached files and skip the 19-hour re-extraction phase entirely.

---

## 📊 Outputs Guide
All results are generated in the `outputs/` folder:
- **`crater_lists/research_catalog.csv`**: The master catalog (X, Y, Lat, Lon, Diameter, Freshness).
- **`crater_lists/research_catalog.diam`**: Scientific file for age-dating in Craterstats.
- **`plots/csfd_plot_research.png`**: CSFD curve with Poisson error bars.
- **`plots/density_heatmap.png`**: Spatial density map formatted in kilometers.
- **`overlays/research_final_overlay.png`**: Visual verification of all certified craters on the landing site.

---

## 🤖 For AI Support (Antigravity)
If you are an AI agent assisting the user:
1. **Always verify `config.py`** has the correct IDs from the `data/raw/` folder before starting.
2. **Check the terminal** for logs like `Strip 100/240...`. If it stops moving, the checkpointing ensures you won't lose work.
3. **Multi-View Certification** requires at least **2 images** to produce scientific results.

---
**Author**: Ganesh et al. (2022) Alignment / Developed for Lunar Landing Site Selection.
