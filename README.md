# Lunar Crater Detection System

A research-grade computer vision system for detecting and analyzing craters on the lunar surface.

## Project Description

This system provides a modular pipeline for processing lunar imagery, detecting crater candidates using shadow-highlight pairs, fitting geometric models to candidates, and refining results using template matching. It also includes tools for Crater Size-Frequency Distribution (CSFD) analysis.

## Folder Structure

```
crater_project/
│
├── data/               # Input data storage
│   ├── raw/            # Original source images
│   ├── processed/      # Normalized and cropped images
│
├── src/                # Source code modules
│   ├── __init__.py
│   ├── preprocess.py   # Image loading and preparation
│   ├── guide_params.py # Parameter estimation
│   ├── detection.py    # Candidate detection
│   ├── fitting.py      # Geometric fitting
│   ├── pixel_flagging.py # Duplicate prevention
│   ├── templates.py    # Template matching logic
│   ├── matching.py     # Multi-image matching
│   ├── csfd.py         # Statistical analysis
│   ├── utils.py        # Utility functions
│
├── outputs/            # Pipeline products
│   ├── crater_lists/   # CSV/JSON lists of detected craters
│   ├── plots/          # CSFD and analysis plots
│   ├── overlays/       # Images with detected craters drawn
│
├── main.py             # Main execution script
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
└── config.py           # Configuration and hyperparameters
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd crater_project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Key Research Implementation (Ganesh et al., 2022)

The system is now fully implemented and aligned with the methodologies described in the research paper *"Automated precision counting of very small craters at lunar landing sites"*.

### **Advanced Features:**
- **Iterative Sub-pixel Fitting**: Refines crater centers and diameters using a contrast-maximization algorithm with 0.5-pixel precision.
- **Freshness Classification**: Automatically categorizes craters into five freshness classes (**Prominent, Sharp, Distinct, Faint, Vague**) based on photometric analysis.
- **Multi-Image Certification**: Uses robust matching across multiple views (w/ XY Discrepancy Map correction) to eliminate false positives.
- **Enhanced CSFD**: Generates log-log cumulative size-frequency plots with standardized **sqrt(N) error bars**.
- **Spatial Density Maps**: Visualizes crater concentrations across the landing site.

## How to Run

To run the full detection and analysis pipeline:

```bash
python main.py
```

*The pipeline will process images in `data/raw`, generate certified catalogs in `outputs/crater_lists`, and produce scientific plots in `outputs/plots`.*

## License

Research Use Only.
