<div align="center">
  
# 🌔 CraterX: Precision Lunar Regolith Mapper

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Science: Planetary](https://img.shields.io/badge/Science-Planetary_Geology-orange.svg)]()

**A research-grade, memory-efficient computer vision pipeline for detecting, measuring, and morphologically classifying millions of micro-craters in high-resolution LROC NAC imagery.**

</div>

---

## 📖 Table of Contents
- Overview & Capabilities  
- Theoretical Alignment  
- Folder Structure  
- Installation & Setup  
- Execution Guide  
- Scientific Outputs  

---

## 🚀 Overview & Capabilities

CraterX is engineered to process massive, multi-gigabyte 16-bit GeoTIFFs from the Lunar Reconnaissance Orbiter without requiring supercomputer hardware. It uses localized, physics-based contrast maximization instead of global thresholding.

**Key Capabilities:**
- Massive Scalability: Detects 1.3+ million micro-craters  
- Sub-Pixel Precision: Uses 0.5-pixel refinement  
- Scale-Invariant Freshness: Diameter-normalized contrast  
- Efficient Matching: KD-Tree + Phase Correlation (log N)

---

## 🔬 Theoretical Alignment

Aligned with Ganesh et al. (2022) – Automated precision counting of very small craters.

Implements:
- Local contrast detection  
- Sun-direction guided search  
- Sub-pixel refinement  
- Template alignment  

---

## 📂 Folder Structure

CraterX/
├── data/  
├── outputs/  
│   ├── checkpoints/  
│   ├── crater_lists/  
│   ├── overlays/  
│   └── plots/  
├── src/  
├── scripts/  
├── main.py  
├── config.py  
└── requirements.txt  

---

## 💻 Installation & Setup

git clone https://github.com/rohit02k5/CraterX.git  
cd CraterX  
python -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  

---

## ⚙️ Execution Guide

python main.py  

---

## 📊 Scientific Outputs

### Visual Overlay

outputs/overlays/research_overlay_FULL.png  

<img width="1744" height="872" alt="Screenshot 2026-04-28 151951" src="https://github.com/user-attachments/assets/16202323-3535-4af0-88da-ac95ebc8955a" />


<img width="1179" height="838" alt="Screenshot 2026-04-28 152015" src="https://github.com/user-attachments/assets/ebfd0d14-9967-4660-b907-9d7d65810c0e" />


<img width="1720" height="909" alt="Screenshot 2026-04-28 152200" src="https://github.com/user-attachments/assets/bc0ab0c9-ebd7-4d67-b5c2-5a21de50a63a" />


- Displays detected craters  
- Validates geometric fitting  
- Shows sub-pixel precision  

---

---

## 🧠 Key Highlights

- Memory-efficient processing  
- High-precision detection  
- Multi-view validation  
- Scientifically accurate outputs  

---

Developed for Lunar Surface Analysis and Landing Site Evaluation
