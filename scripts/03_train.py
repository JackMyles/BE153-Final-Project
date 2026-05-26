"""Stage 3 — fit the baseline and cortisol-augmented models.

Outputs:
  * ``results/metrics.json`` – pooled metrics for each model
  * ``results/per_subject.csv`` – per-subject AUROC for every model
  * ``results/coefficients.csv`` – averaged feature weights
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model import (  # noqa: E402
    fit_loso,
    baseline_features,
    augmented_features,
    average_coefficients,
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--features", default=str(ROOT / "cache" / "features.parquet"))
    ap.add_argument("--csv-fallback", default=str(ROOT / "cache" / "features.csv"))
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()

    feat_path = Path(args.features)
    if feat_path.exists():
        try:
            df = pd.read_parquet(feat_path)
        except Exception:
            df = pd.read_csv(args.csv_fallback)
    else:
        df = pd.read_csv(args.csv_fallback)

    print(f"Loaded features: {df.shape[0]} windows × {df.shape[1]} columns")
    print(f"Subjects: {sorted(df['subject'].unique())}")
    print(f"Stress windows: {int((df['is_stress']==1).sum())} / {len(df)}")

    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)

    baseline = fit_loso(df, baseline_features(), name="baseline (wearable only)")
    augmented = fit_loso(df, augmented_features(), name="augmented (+ cortisol)")
    # Just-cortisol model is informative for the slides.
    cort_only = fit_loso(df, ["cort_mean", "cort_slope", "cort_auc"],
                         name="cortisol only")

    metrics = {
        baseline.name: baseline.metrics(),
        augmented.name: augmented.metrics(),
        cort_only.name: cort_only.metrics(),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print("\n=== Pooled metrics (LOSO) ===")
    print(json.dumps(metrics, indent=2))

    # Per-subject AUROC table
    rows = []
    for r in [baseline, augmented, cort_only]:
        for s, a in r.per_subject_auroc().items():
            rows.append({"model": r.name, "subject": s, "auroc": a})
    per_sub = pd.DataFrame(rows)
    per_sub.to_csv(out_dir / "per_subject.csv", index=False)

    # Coefficients table
    coef_df = pd.DataFrame({
        baseline.name: average_coefficients(baseline),
        augmented.name: average_coefficients(augmented),
    })
    coef_df.to_csv(out_dir / "coefficients.csv")
    print("\nTop baseline features by |β|:")
    print(coef_df[[baseline.name]].dropna().reindex(coef_df[baseline.name].abs()
          .sort_values(ascending=False).index).head(8))

    # Save the model results object for the plotting stage.
    import pickle
    with open(out_dir / "fits.pkl", "wb") as fh:
        pickle.dump(dict(baseline=baseline, augmented=augmented,
                         cortisol_only=cort_only), fh)
    print(f"\nWrote {out_dir/'metrics.json'}, per_subject.csv, coefficients.csv, fits.pkl")


if __name__ == "__main__":
    main()
