"""Stage 4 — produce all figures used in the slides.

Reads cached features and trained-model results and writes PNGs to
``figures/``.
"""
from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load_wesad import load_cached  # noqa: E402
from src.plots import (  # noqa: E402
    plot_wrist_signals,
    plot_cortisol_simulation,
    plot_feature_distributions,
    plot_roc,
    plot_confusions,
    plot_per_subject_auroc,
    plot_coefficients,
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", default=str(ROOT / "cache"))
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--out", default=str(ROOT / "figures"))
    ap.add_argument("--example-subject", default="S2")
    args = ap.parse_args()

    cache_dir = Path(args.cache); results_dir = Path(args.results)
    fig_dir = Path(args.out); fig_dir.mkdir(parents=True, exist_ok=True)

    # Pick an example subject for the per-subject panels.
    example_path = cache_dir / f"{args.example_subject}_wrist.npz"
    if not example_path.exists():
        # Fallback: first available subject.
        candidates = sorted(cache_dir.glob("S*_wrist.npz"))
        example_path = candidates[0]
    rec = load_cached(example_path)

    print(f"Plotting wrist signals for {rec.subject} ...")
    plot_wrist_signals(rec, fig_dir / "fig1_wrist_signals.png")

    print(f"Plotting cortisol simulation for {rec.subject} ...")
    plot_cortisol_simulation(rec, fig_dir / "fig2_cortisol_simulation.png")

    feats_path = cache_dir / "features.parquet"
    try:
        df = pd.read_parquet(feats_path)
    except Exception:
        df = pd.read_csv(cache_dir / "features.csv")
    print(f"Plotting feature distributions ({df.shape[0]} windows)...")
    plot_feature_distributions(df, fig_dir / "fig3_feature_distributions.png")

    print("Loading fitted models...")
    with open(results_dir / "fits.pkl", "rb") as fh:
        fits = pickle.load(fh)
    baseline = fits["baseline"]; augmented = fits["augmented"]
    cort_only = fits["cortisol_only"]

    plot_roc([baseline, augmented, cort_only], fig_dir / "fig4_roc.png")
    plot_confusions([baseline, augmented], fig_dir / "fig5_confusions.png")
    plot_per_subject_auroc([baseline, augmented], fig_dir / "fig6_per_subject_auroc.png")
    plot_coefficients([baseline, augmented], fig_dir / "fig7_coefficients.png")
    print(f"Figures saved to {fig_dir}/")


if __name__ == "__main__":
    main()
