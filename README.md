# Hidden Markov Model for Human Activity Recognition

**Course**: Machine Learning — Formative 2  
**Group Members**: Elissa Twizeyimana & Uwingabire Caline  
**Date**: March 2026

---

## Overview

This project implements a Hidden Markov Model (HMM) from scratch to classify human physical activities using smartphone inertial measurement unit (IMU) data. Each activity is modelled as a sequence of hidden sub-states, and the Viterbi algorithm is used to decode the most likely state path. Parameters are learned via the Baum-Welch expectation-maximisation algorithm.

**Achieved accuracy: 100% on unseen test data.**

---

## Activities Classified

| Activity | Description |
|---|---|
| Still | Phone placed flat on a surface — no movement |
| Standing | Held at waist level, minor postural sway |
| Walking | Consistent walking pace |
| Jumping | Continuous repeated jumps |

---

## Dataset

| Property | Value |
|---|---|
| Total recordings | 120 (30 per activity) |
| Device | iPhone 12 Pro (both members) |
| Sampling rate | 50 Hz (20 ms interval) |
| Sensors | Accelerometer (x, y, z) + Gyroscope (x, y, z) |
| Format | CSV files per session |

Each recording is 5–10 seconds long. Both group members collected 60 recordings each, using the same device model at the same sampling rate, so no resampling was required.

### Data Folder Structure

```
Data/
├── Jumping/
│   ├── 1/  (Accelerometer.csv, Gyroscope.csv)
│   ├── 2/
│   └── ... (30 sessions)
├── Standing/  (same structure)
├── Still/     (same structure)
└── Walking/   (same structure)
```

---

## Feature Extraction

Each recording is divided into **1-second sliding windows** (50 samples at 50 Hz) with **50% overlap** (25-sample stride). This window size captures at least one complete cycle of every target activity at 50 Hz.

**72 features per window:**

| Domain | Features | Per axis | Axes | Total |
|---|---|---|---|---|
| Time-domain | mean, std, min, max, range, RMS, zero-crossing rate | 7 | 6 (accel + gyro × xyz) | 42 |
| Time-domain (combined) | SMA, vector magnitude mean/std, inter-axis correlations (xy, xz, yz) | — | per sensor | 12 |
| Frequency-domain | dominant frequency, spectral energy, spectral entropy | 3 | 6 | 18 |

All features are **Z-score normalised** using statistics computed from training data only to prevent data leakage.

---

## Model Architecture

- **One GaussianHMM per activity class** (4 models total)
- **4 hidden states** per model, representing activity sub-phases
- **Diagonal covariance** — prevents numerical underflow with limited training data
- **Baum-Welch EM training** with convergence criterion `|ΔLL| < 1e-3`
- **Log-space Viterbi decoding** — avoids floating-point underflow over long sequences
- **Classification**: test sequence scored against all 4 models; highest log-likelihood wins

---

## Results

| Activity | Sensitivity | Specificity | Precision | F1 Score |
|---|---|---|---|---|
| Jumping | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Standing | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Still | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Walking | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

- **Overall test accuracy: 100%** (24/24 unseen sequences correctly classified)
- Train/test split: 96 training sequences / 24 test sequences (80/20 stratified)

---

## Repository Contents

| File | Description |
|---|---|
| `HMM_Activity_Recognition.ipynb` | Full implementation — data loading, feature extraction, HMM, evaluation, visualisations |
| `Data/` | 120 labelled CSV recordings (30 per activity) |
| `Report.pdf` | 4–5 page project report (see submission) |

---

## How to Run

1. **Upload this repository folder to Google Drive**
2. Open `HMM_Activity_Recognition.ipynb` in **Google Colab**
3. In Cell 5, update `base_path` to match your Drive folder path, e.g.:
   ```python
   base_path = '/content/drive/MyDrive/Hidden-Markov-Models/Data'
   ```
4. Run all cells (`Runtime → Run all`)

**Dependencies** (all pre-installed in Colab):
`numpy`, `pandas`, `matplotlib`, `seaborn`, `scipy`, `scikit-learn`

---

## Task Allocation

| Task | Responsible |
|---|---|
| Data collection (60 recordings each) | Elissa Twizeyimana & Uwingabire Caline |
| Feature extraction pipeline | Elissa Twizeyimana & Uwingabire Caline |
| GaussianHMM class (Viterbi + Baum-Welch) | Elissa Twizeyimana & Uwingabire Caline |
| Evaluation, confusion matrix, visualisations | Elissa Twizeyimana & Uwingabire Caline |
| Report writing | Elissa Twizeyimana & Uwingabire Caline |
