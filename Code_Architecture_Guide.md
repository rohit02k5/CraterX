# CraterX: Code Architecture & System Explanation Guide

This document describes the structure of the CraterX codebase and explains where and how each algorithm is implemented. It is intended to provide a clear, system-level understanding of the pipeline.

---

## 1. `main.py` (Pipeline Orchestrator)

### Functionality
Acts as the central controller of the pipeline, coordinating data flow between modules.

### Description
- To process large-scale GeoTIFF datasets (up to 4GB) efficiently without exhausting system memory, `main.py` implements a chunking strategy. The function `split_into_strips` divides the image into overlapping `2000×2000` pixel tiles for sequential processing.  
- A checkpointing mechanism is integrated to improve fault tolerance. After processing each tile, intermediate detection results are stored in JSON format. This enables the pipeline to resume from the last completed step in case of interruption, avoiding recomputation.

---

## 2. `src/detection.py` (Initial Detection Module)

### Functionality
Performs detection of shadowed and illuminated regions corresponding to potential craters.

### Description
- The `detect_lowlights` function avoids global thresholding due to non-uniform illumination in planetary imagery. Instead, it evaluates local contrast by comparing the shadow mean with the surrounding local mean. Regions with insufficient contrast are rejected.  
- The `find_highlight` function uses prior knowledge of solar illumination. Using the solar azimuth vector (`guide_dir`), it predicts the expected location of the illuminated crater rim, reducing search space and improving detection accuracy.

---

## 3. `src/fitting.py` (Sub-Pixel Refinement Module)

### Functionality
Refines initial detections to obtain precise crater geometry.

### Description
- Pixel-level detections are refined using a sub-pixel optimization approach in `fit_crater`. Candidate crater centers are evaluated on a fine grid with `0.5-pixel` resolution.  
- For each candidate, `evaluate_contrast_fast` computes a contrast score by dividing the crater into sunlit and shadowed halves using the solar direction vector.  
- The difference in mean intensity between these halves is calculated, and the configuration with the maximum contrast is selected as the optimal crater center and diameter.

---

## 4. `src/templates.py` (Morphological Analysis & Refinement)

### Functionality
Handles crater classification and template-based refinement.

### Description
- The `classify_freshness` function estimates crater degradation using normalized contrast defined as `(max_intensity - min_intensity) / diameter`. This ensures scale-invariant classification across different crater sizes, aligned with Basilevsky categories (e.g., Prominent to Vague).  
- The `build_class_templates` function generates representative templates by averaging aligned crater patches within each class.  
- The `refine_with_freshness_templates` function applies normalized cross-correlation (`cv2.matchTemplate`) to refine crater positions by aligning detections with these templates.

---

## 5. `src/matching.py` (Multi-View Verification Module)

### Functionality
Validates detections across multiple images to reduce false positives.

### Description
- The `register_images_global` function aligns multiple satellite images using phase correlation (`cv2.phaseCorrelate`) on downscaled versions to estimate global translational offsets.  
- The `match_craters_multi_view_optimized` function projects detections into a common coordinate frame. To avoid O(N²) complexity, a `cKDTree` (SciPy) is used to perform efficient spatial queries in O(log N) time.  
- A fallback mechanism (`MIN_VIEWS_FOR_CERT`) ensures robustness when image overlap is limited by preserving detections using a union-based approach.

---

## 6. `src/csfd.py` & `src/visualization.py` (Scientific Output Modules)

### Functionality
Generates scientific outputs and validation plots.

### Description
- The `csfd.py` module computes the **Cumulative Size-Frequency Distribution (CSFD)** of detected craters.  
- Crater counts are normalized by the mapped surface area (in km²) and plotted on log-log axes.  
- Statistical uncertainty is represented using Poisson error bars (`±√N`).  
- Outputs are exported in `.diam` format, ensuring compatibility with standard planetary science tools such as *Craterstats*.

---

## Summary of Pipeline Flow

1. Large GeoTIFF is split into manageable tiles (`main.py`)  
2. Shadow and highlight regions are detected (`detection.py`)  
3. Crater geometry is refined at sub-pixel accuracy (`fitting.py`)  
4. Craters are classified and refined using templates (`templates.py`)  
5. Multi-image validation removes false positives (`matching.py`)  
6. Final scientific outputs and distributions are generated (`csfd.py`, `visualization.py`)

---

## Key Design Principles

- **Memory Efficiency:** Chunk-based processing of large datasets  
- **Robustness:** Checkpointing to prevent data loss  
- **Accuracy:** Sub-pixel refinement and illumination-aware detection  
- **Scalability:** Efficient spatial indexing using `cKDTree`  
- **Scientific Validity:** Standard CSFD outputs with uncertainty estimation  

---
