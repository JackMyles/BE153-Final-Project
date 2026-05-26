# Wearable Stress Detection: WESAD + Cortisol Augmentation

BE 153 final project. Builds a quantitative stress-detection model from
the wrist-worn-wearable signals in the WESAD dataset, then shows how
adding a (simulated) continuous cortisol channel — the kind a next-gen
electrochemical sweat sensor could provide — improves the model.

## Project structure

```
.
├── WESAD/                       Existing dataset (15 subjects: S2..S17, no S1/S12)
├── src/
│   ├── load_wesad.py            Extract wrist signals + labels from each S*.pkl
│   ├── features.py              60-s sliding-window physiological features
│   ├── cortisol_sim.py          HPA-axis kinetic cortisol simulator
│   ├── model.py                 Logistic-regression baseline + augmented model
│   └── plots.py                 Figure generation
├── scripts/
│   ├── 01_preprocess.py         .pkl  ->  cache/SX_wrist.npz
│   ├── 02_features.py           cache/SX_wrist.npz  ->  cache/features.parquet
│   ├── 03_train.py              Trains both models, writes results/metrics.json
│   └── 04_figures.py            Writes figures/*.png used in the presentation
├── cache/                       (generated)  per-subject NumPy arrays + feature table
├── figures/                     (generated)  PNGs for slides
├── results/                     (generated)  metrics.json, classification report
├── presentation_notes.md        Slide-by-slide speaker notes (10–12 slides, ~10 min)
└── requirements.txt
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Stage 1 – decode every WESAD .pkl into a small, fast cache (~1–2 min/subj)
python scripts/01_preprocess.py

# Stage 2 – sliding-window features for every subject
python scripts/02_features.py

# Stage 3 – fit baseline + cortisol-augmented models, leave-one-subject-out CV
python scripts/03_train.py

# Stage 4 – figures used in the slides
python scripts/04_figures.py
```

Total runtime end-to-end is ~10–15 min on a laptop. Each stage caches its
output so individual stages can be re-run cheaply.

## Mathematical summary

Per 60-s window, features `x ∈ R^d` are extracted from EDA, BVP-derived
HR/HRV, skin temperature, and wrist ACC. A logistic stress index is

  S(x) = β₀ + βᵀ x,        P(stress | x) = σ(S(x)) = 1 / (1 + e^{-S(x)}).

Coefficients β are fit by L2-regularised logistic regression with
leave-one-subject-out cross-validation. The **augmented** model adds a
cortisol feature `c(t)`:

  S'(x, c) = β₀' + β'ᵀ x + β_c · z(c(t)).

Cortisol concentration is simulated from a first-order HPA-axis model

  dC/dt = –λ(C – C_basal) + k_s · u(t),

where `u(t)` is a binary "perceived-stress" drive (the WESAD stress
label), `λ = ln 2 / T½` with `T½ ≈ 66 min`, and `k_s` is chosen so
peak cortisol reaches ~9× basal during sustained acute stress, matching
Cay et al. 2018 (NCI). Inter-subject log-normal variability and ~10 %
sensor noise are added.

## Data note

The script reads every `WESAD/S*/S*.pkl`. Each pickle is ~950 MB but is
loaded once and converted to a small per-subject `.npz` (≈ 30 MB) that
holds only wrist BVP / EDA / TEMP / ACC and the downsampled label
vector. After Stage 1 you don't need to touch the pickles again.
