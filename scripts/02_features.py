"""Stage 2 — sliding-window features for every subject + simulated cortisol.

Reads ``cache/SX_wrist.npz`` (produced by 01_preprocess.py) and writes
``cache/features.parquet`` with one row per 60-s window. Cortisol
features are appended in the same pass so the augmented model just
selects extra columns.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load_wesad import load_cached  # noqa: E402
from src.features import extract_features  # noqa: E402
from src.cortisol_sim import simulate_cortisol, window_cortisol_features, CORTISOL_FEATURE_NAMES  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", default=str(ROOT / "cache"))
    ap.add_argument("--out", default=str(ROOT / "cache" / "features.parquet"))
    ap.add_argument("--csv", default=str(ROOT / "cache" / "features.csv"),
                    help="Also write a CSV copy (handy without pyarrow)")
    args = ap.parse_args()

    cache_dir = Path(args.cache)
    npzs = sorted(cache_dir.glob("S*_wrist.npz"),
                  key=lambda p: int(p.stem.split("_")[0].lstrip("S")))
    if not npzs:
        print(f"No cached subjects under {cache_dir}. Run 01_preprocess.py first.")
        sys.exit(1)

    all_rows = []
    for i, p in enumerate(npzs, 1):
        t0 = time.time()
        rec = load_cached(p)
        feats = extract_features(rec)
        # Cortisol
        cort = simulate_cortisol(rec.label, rec.fs, subject=rec.subject)
        c_feats = window_cortisol_features(cort, rec.fs, feats["t_center_s"].values)
        for k, name in enumerate(CORTISOL_FEATURE_NAMES):
            feats[name] = c_feats[:, k]
        all_rows.append(feats)
        n_pos = int((feats["is_stress"] == 1).sum())
        n_tot = len(feats)
        print(f"  [{i:>2}/{len(npzs)}] {rec.subject}: {n_tot} windows, "
              f"{n_pos} stress ({100*n_pos/max(n_tot,1):4.1f}%)  "
              f"({time.time()-t0:4.1f} s)")

    df = pd.concat(all_rows, ignore_index=True)
    out_path = Path(args.out); out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_parquet(out_path, index=False)
        print(f"Wrote {out_path}  shape={df.shape}")
    except Exception as exc:
        print(f"Parquet write failed ({exc!r}); CSV will still be written.")

    if args.csv:
        df.to_csv(args.csv, index=False)
        print(f"Wrote {args.csv}")


if __name__ == "__main__":
    main()
