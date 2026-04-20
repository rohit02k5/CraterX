# 🌔 Lunar Crater Detection System (RegolithMapper)

A research-grade, memory-efficient computer vision pipeline for detecting and measuring lunar craters in high-resolution LROC NAC imagery. This system is mathematically aligned with the methodology of **Ganesh et al. (2022)**.

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Folder Structure](#-folder-structure)
- [Key Features](#-key-features)
- [Prerequisites & Installation](#-prerequisites--installation)
- [Data Preparation](#-data-preparation)
- [Configuration](#-configuration)
- [Running the Pipeline](#-running-the-pipeline)
- [Outputs Guide](#-outputs-guide)
- [Crash Protection & Resuming](#-crash-protection--resuming)

---

## 🚀 Overview
This pipeline is designed for long-running, mission-critical scientific analysis. It is optimized for high-end workstations and features a robust "Quick Resume" system to protect against hardware restarts or crashes.

---

## 📂 Folder Structure

```text
RegolithMapper/
│
├── data/                   # Place your data here (ignored by Git to save space)
│   └── raw/                # Raw 16-bit GeoTIFF LROC NAC images
│
├── outputs/                # All generated results (ignored by Git)
│   ├── checkpoints/        # Auto-saved detection checkpoints for crash recovery
│   ├── crater_lists/       # CSV and .diam master catalogs
│   ├── overlays/           # Visual verifications of certified craters
│   └── plots/              # CSFD curves and density heatmaps
│
├── src/                    # Core source code modules
│   ├── csfd.py             # Cumulative Size-Frequency Distribution plotting
│   ├── detection.py        # Core crater detection algorithms
│   ├── fitting.py          # Sub-pixel diameter solvers and ellipse fitting
│   ├── guide_params.py     # Guide templates for detection
│   ├── matching.py         # Multi-view UNION-set matching engine
│   ├── pixel_flagging.py   # Pixel intensity analysis & flagging
│   ├── preprocess.py       # Image preprocessing and enhancement
│   ├── roi.py              # Region of Interest handling
│   ├── templates.py        # Template generation for crater matching
│   ├── utils.py            # Utility functions for geospatial conversions
│   └── visualization.py    # Map overlay and heatmap generation
│
├── scripts/                # Utility and synthetic data generation scripts
│   ├── check_shapes.py     # Script to verify data shapes
│   └── generate_synthetic_data.py # Generate synthetic LROC data for testing
│
├── main.py                 # The main entry point to run the pipeline
├── config.py               # Centralized configuration and hyperparameter tuning
├── requirements.txt        # Python dependencies
├── .gitignore              # Files to ignore in Git (caches, data, outputs)
└── README.md               # Project documentation (this file)
```

---

## 🧪 Key Features
- **16-Bit Photometric Integrity**: Preserves full LROC NAC dynamic range (0–65535 DN) using `tifffile` and `rasterio`.
- **Multi-View Certification**: Uses a **UNION-set matching engine** to cross-reference detections across multiple orbital views, eliminating false positives and noise.
- **Sub-Pixel Diameter Solver**: Employs an iterative contrast-maximization algorithm to achieve **0.5-pixel precision**.
- **Geospatial Support**: Automatically converts X/Y pixel coordinates to **Latitude and Longitude** using GeoTIFF affine transforms.
- **CSFD & Chronology**: Generates Cumulative Size-Frequency Distribution plots and exports `.diam` files compatible with **Craterstats**.

---

## 💻 Prerequisites & Installation

### 1. Requirements
Ensure your machine has **Python 3.9+** and a dedicated GPU is recommended (for general system performance, as the code is CPU-multithreaded and vector-optimized for massive datasets).

### 2. Setup Guide
```bash
# Clone the repository
git clone <repository-url>
cd RegolithMapper

# Create a virtual environment (Recommended)
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📦 Data Preparation
Place your raw **16-bit GeoTIFF** LROC NAC images in the `data/raw/` directory.
- The system expects `.tif` or `.tiff` files.
- Each image must have internal GeoTIFF metadata if you want Latitude/Longitude output.

---

## ⚙️ Configuration (`config.py`)
Before running the pipeline, tune the following constants to your target landing site in `config.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `PIXEL_SIZE_METERS` | `0.5` | Native scale of LROC NAC. |
| `ROI_RADIUS_METERS` | `500` | Radius of the search area around the landing site. |
| `IMAGE_METADATA` | `{...}` | **CRITICAL**: Add your image IDs, sun angles, and directions here to skip 8+ hours of solar estimation. |
| `MIN_VIEWS_FOR_CERT`| `2` | Number of views required to certify a crater (avoids false positives). |

---

## 🏃 Running the Pipeline
Run the main script from the root directory:
```bash
python main.py
```
This will process the images in `data/raw/`, run the detection algorithms, match overlapping craters, and generate outputs.

---

## 📊 Outputs Guide
All scientific results are generated in the `outputs/` folder:
- **`outputs/crater_lists/research_catalog.csv`**: The master catalog containing X, Y, Lat, Lon, Diameter, and Freshness.
- **`outputs/crater_lists/research_catalog.diam`**: Scientific file for age-dating in Craterstats.
- **`outputs/plots/csfd_plot_research.png`**: CSFD curve with Poisson error bars.
- **`outputs/plots/density_heatmap.png`**: Spatial density map formatted in kilometers.
- **`outputs/overlays/research_final_overlay.png`**: Visual verification overlay of all certified craters on the landing site.

---

## 🛡️ Crash Protection & Resuming
Detections take approximately **8-10 hours** for a full-resolution 4-image cohort.
- **Auto-Save**: The system continuously saves candidates in `outputs/checkpoints/` after each image finishes processing.
- **Resuming**: If the script is interrupted (e.g., power loss, system crash), simply run `python main.py` again. It will automatically detect the cached files and resume from where it left off, potentially saving up to 19 hours of re-extraction.

---
**Author**: SVS Rohit
