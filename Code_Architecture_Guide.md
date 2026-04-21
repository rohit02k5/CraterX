# CraterX: Code Architecture & Professor Defense Guide

Use this document to study the exact structure of the codebase and confidently explain to your professor *where* and *how* every algorithm is implemented.

## 1. `main.py` (The Orchestrator)
**What it does:** This is the central nervous system. It does not hold heavy math; instead, it coordinates the pipeline.
**How to explain it:** 
* "Professor, to handle massive 4GB GeoTIFFs without crashing the RAM, `main.py` uses a chunking methodology. It calls `split_into_strips` to break the image into 2000x2000 overlapping grids."
* "It also contains a robust Checkpointing system. After processing an image, it saves the raw detections to JSON. If the power fails, the script resumes instantly without losing 10 hours of work."

## 2. `src/detection.py` (The Initial Scanner)
**What it does:** Implements the shadow and highlight detection.
**How to explain it:** 
* "In `detect_lowlights`, I didn't use a simple `cv2.threshold` because global illumination varies. Instead, I calculate the `shadow_mean` and compare it to the `local_mean` of the surrounding pixels. If the contrast difference isn't high enough, it's rejected."
* "In `find_highlight`, the code uses the `guide_dir` (the known solar azimuth vector) to project exactly where the bright sunlit rim *should* be, rather than blindly searching the whole image."

## 3. `src/fitting.py` (The Sub-Pixel Solver)
**What it does:** Refines the crude shadow/highlight pair into an exact mathematical circle.
**How to explain it:** 
* "Professor, native pixel measurements are too crude for accurate age-dating. My `fit_crater` function implements an iterative solver. It creates a grid of hypothetical centers moving in incredibly small `0.5 pixel` steps."
* "For each sub-pixel step, `evaluate_contrast_fast` takes the vector dot-product of the sun direction against the circular mask to separate the 'sunlit half' from the 'shadowed half'. It subtracts the two means to find the highest contrast score. That peak score becomes the final sub-pixel center and diameter."

## 4. `src/templates.py` (Morphology & Refinement)
**What it does:** Handles the "Freshness" classification and the final template-nudging.
**How to explain it:** 
* "To classify how old a crater is, `classify_freshness` extracts a local image patch. It calculates the `max_val - min_val` (the absolute contrast) and divides it by the crater's `diameter`. This normalization ensures that a massive crater and a 3-pixel crater are judged on the exact same scale, mapping them to the standard Basilevsky classes (Prominent to Vague)."
* "Later, `build_class_templates` physically averages the pixels of all detected craters to build 'ideal' visual templates for each freshness class. `refine_with_freshness_templates` then uses Normalized Cross-Correlation (`cv2.matchTemplate`) to snap the crater coordinates perfectly to these ideal shapes."

## 5. `src/matching.py` (Multi-View Certification)
**What it does:** Eliminates false positives by checking multiple images.
**How to explain it:** 
* "To align different satellite passes, `register_images_global` uses Phase Correlation (`cv2.phaseCorrelate`) on downscaled thumbnails to calculate the exact X/Y drift between the images."
* "In `match_craters_multi_view_optimized`, I project the coordinates into a common frame. Because checking millions of craters against each other would take O(N²) time (weeks of processing), I implemented a `cKDTree` from SciPy. This allows the system to execute blazing-fast spatial queries in O(log N) time to find matching overlapping craters."
* "I also implemented a `MIN_VIEWS_FOR_CERT` fallback, which allows the system to perform a 'Union' preservation of unique craters in the event that the satellite strips do not overlap."

## 6. `src/csfd.py` & `src/visualization.py` (Science Outputs)
**What it does:** Generates the final charts and catalogs.
**How to explain it:** 
* "To prove the validity of the data, `csfd.py` plots the Cumulative Size-Frequency Distribution. It normalizes the crater counts by the exact $km^2$ area of the GeoTIFF, plotting them on a standard log-log scale with Poisson error bars ($\pm \sqrt{N}$), generating `.diam` files that are perfectly compatible with professional *Craterstats* software."
