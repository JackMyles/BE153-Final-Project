"""Stage 1 — decode every WESAD .pkl into a small wrist-signal cache.

Run once. Each subject's .pkl (~ 1 GB) is converted into a < 50 MB
``cache/SX_wrist.npz`` containing wrist ACC / BVP / EDA / TEMP and the
downsampled WESAD label vector.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load_wesad import discover_subjects, load_subject, save_record  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wesad", default=str(ROOT / "WESAD"),
                    help="Path to the WESAD root folder")
    ap.add_argument("--out", default=str(ROOT / "cache"),
                    help="Where to write the .npz caches")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    wesad_root = Path(args.wesad)
    cache_dir = Path(args.out); cache_dir.mkdir(parents=True, exist_ok=True)

    pkls = discover_subjects(wesad_root)
    if not pkls:
        print(f"No WESAD pickles found under {wesad_root}")
        sys.exit(1)

    print(f"Found {len(pkls)} subjects.")
    for i, pkl in enumerate(pkls, 1):
        out_path = cache_dir / f"{pkl.stem}_wrist.npz"
        if out_path.exists() and not args.overwrite:
            print(f"  [{i:>2}/{len(pkls)}] {pkl.stem}: cache exists, skip")
            continue
        t0 = time.time()
        rec = load_subject(pkl)
        save_record(rec, out_path)
        n_min = len(rec.label) / rec.fs / 60.0
        print(f"  [{i:>2}/{len(pkls)}] {pkl.stem}: {n_min:5.1f} min wrist data "
              f"-> {out_path.name}  ({time.time()-t0:5.1f} s)")


if __name__ == "__main__":
    main()
