<div align="center">
  
# 🌔 CraterX: Precision Lunar Regolith Mapper

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Science: Planetary](https://img.shields.io/badge/Science-Planetary_Geology-orange.svg)]()

**A research-grade, memory-efficient computer vision pipeline for detecting, measuring, and morphologically classifying millions of micro-craters in high-resolution LROC NAC imagery.**

</div>

---

## 📖 Table of Contents
- [Overview & Capabilities](#-overview--capabilities)
- [Theoretical Alignment](#-theoretical-alignment)
- [Folder Structure](#-folder-structure)
- [Installation & Setup](#-installation--setup)
- [Execution Guide](#-execution-guide)
- [Scientific Outputs](#-scientific-outputs)

---

## 🚀 Overview & Capabilities

CraterX is engineered to process massive, multi-gigabyte 16-bit GeoTIFFs from the Lunar Reconnaissance Orbiter without requiring supercomputer hardware. It abandons brittle global thresholding in favor of localized, physics-based contrast maximization.

**Key Capabilities:**
- **Massive Scalability:** Successfully detects and catalogs **1.3+ million** micro-craters across disjoint LROC strips using localized grid-chunking.
- **Sub-Pixel Precision:** Employs an iterative contrast-maximization solver that steps through the image grid at 0.5-pixel intervals to achieve mathematical precision beyond native camera resolution.
- **Scale-Invariant Freshness:** Dynamically extracts localized patches and computes diameter-normalized contrast ratios to classify craters into standard morphological degradation classes (Prominent, Sharp, Distinct, Faint, Vague).
- **Multi-View KD-Tree Matching:** Utilizes SciPy spatial `cKDTrees` and Phase Correlation to cross-reference craters across multiple orbital views in $O(\log N)$ time, featuring a robust "Union Fallback" for disjoint datasets.

---

## 🔬 Theoretical Alignment

This pipeline is mathematically and architecturally aligned with the methodologies described in **Ganesh et al. (2022)** *(Automated precision counting of very small craters at lunar landing sites)*. 

It implements the core tenets of local-contrast shadow detection, sun-vector guided highlight searching, sub-pixel centering, and dynamic template refinement. *Note: Seeded Search (False Negative Recovery) was intentionally omitted from this implementation to preserve RAM efficiency on consumer-grade hardware.*

---

## 📂 Folder Structure

```text
CraterX/
│
├── data/                   # (Ignored by Git)
│   └── raw/                # Place raw 16-bit GeoTIFF LROC NAC images here
│
├── outputs/                # All generated scientific results (Ignored by Git)
│   ├── checkpoints/        # Auto-saved detection caches for crash-recovery
│   ├── crater_lists/       # CSV catalogs containing X, Y, Lat, Lon, D_m, Freshness
│   ├── overlays/           # Massive, high-res visual HUD verification images
│   └── plots/              # CSFD curves (.diam & .png) and spatial heatmaps
│
├── src/                    # Core Algorithms
│   ├── preprocess.py       # GeoTIFF handling, scaling, and chunking
│   ├── detection.py        # Local contrast shadow/highlight detection
│   ├── fitting.py          # Iterative Sub-pixel contrast-maximization solver
│   ├── templates.py        # Freshness classification & Template refinement
│   ├── matching.py         # Multi-view global registration & KD-Tree Union matching
│   ├── pixel_flagging.py   # Exclusion masking for dense regions
│   ├── roi.py              # Landing Zone Region of Interest handlers
│   ├── csfd.py             # Size-Frequency Distribution plotting & Craterstats prep
│   ├── visualization.py    # Spatial density heatmap generation
│   └── utils.py            # Geospatial affine translations
│
├── scripts/                # Maintenance and synthetic testing
│   ├── update_checkpoints.py # Retrofits freshness data into existing caches
│   └── ...
│
├── main.py                 # Pipeline Orchestrator
├── config.py               # Hyperparameters and constants (MIN_VIEWS, ROI size)
└── requirements.txt        # Python dependency manifest
```

---

## 💻 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/rohit02k5/CraterX.git
   cd CraterX
   ```

2. **Create a Virtual Environment (Highly Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare your Data**
   Place your high-resolution 16-bit `.tif` LROC NAC images into the `data/raw/` folder.

---

## ⚙️ Execution Guide

Before running, configure your Landing Zone constraints in `config.py`:
- `PIXEL_SIZE_METERS`: Native resolution (Default: 0.5)
- `ROI_RADIUS_METERS`: Target landing zone size.
- `MIN_VIEWS_FOR_CERT`: Set to `1` to enable Union Fallback for disjoint strips, or `2` for strict intersection certification.

**To execute the entire pipeline:**
```bash
python main.py
```
*Note: Initial detection on gigabyte-sized images can take several hours. The system automatically caches progress to `outputs/checkpoints/`. If your system crashes, simply rerun `main.py` to instantly resume from the exact point of failure.*

---

## 📊 Scientific Outputs

Upon completion, CraterX generates a comprehensive suite of data in the `outputs/` directory:

1. **`research_catalog_FULL.csv`**: The master database containing sub-pixel X/Y coordinates, true Latitude/Longitude, Diameter in meters, and Morphological Freshness.
2. **`csfd_plot_FULL.diam`**: A Craterstats-ready file tracking cumulative density per $km^2$ with standard Poisson error bars.
3. **`research_overlay_FULL.png`**: A massive visual diagnostic output overlaying high-tech HUD targeting reticles onto the raw imagery to visually verify every single detection.
4. **`density_heatmap_FULL.png`**: A topological spatial map indicating crater density severity across the landing zone.

---
*Developed for advanced Lunar Landing Site Selection and Surface Age-Dating Analysis.*
