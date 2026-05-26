"""Load WESAD pickle files and extract a compact wrist + label cache.

Each ``WESAD/SX/SX.pkl`` is a dictionary with this layout::

    {
        "subject": "SX",
        "signal": {
            "chest": {"ACC", "ECG", "EDA", "EMG", "Resp", "Temp"} @ 700 Hz,
            "wrist": {
                "ACC":  (N, 3) @ 32 Hz,
                "BVP":  (N, 1) @ 64 Hz,
                "EDA":  (N, 1) @  4 Hz,
                "TEMP": (N, 1) @  4 Hz,
            },
        },
        "label": (N_700,) ints in {0..7}  @ 700 Hz,
    }

We only keep the wrist signals (what an Empatica-E4-class wearable can
report) and a label vector downsampled to 4 Hz, which is the slowest
wrist signal. Each subject is written as ``cache/SX_wrist.npz``.
"""
from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np

WRIST_FS = {"ACC": 32, "BVP": 64, "EDA": 4, "TEMP": 4}
LABEL_FS_RAW = 700  # Hz, the RespiBAN sample rate
TARGET_FS = 4       # Hz, slowest wrist channel; everything is resampled here

LABEL_NAMES = {
    0: "transient",
    1: "baseline",
    2: "stress",
    3: "amusement",
    4: "meditation",
}


@dataclass
class WristRecord:
    """A subject's wrist signals and labels, all resampled to ``TARGET_FS``."""

    subject: str
    fs: int
    acc: np.ndarray   # (N, 3)
    bvp: np.ndarray   # (N,)      ← decimated to TARGET_FS for plotting only
    bvp_64: np.ndarray  # (N_64,) ← kept at 64 Hz for HR/HRV
    eda: np.ndarray   # (N,)
    temp: np.ndarray  # (N,)
    label: np.ndarray  # (N,) int

    def time(self) -> np.ndarray:
        return np.arange(len(self.label)) / self.fs


def _decimate_to(x: np.ndarray, src_fs: int, dst_fs: int) -> np.ndarray:
    """Block-average decimation from ``src_fs`` Hz to ``dst_fs`` Hz."""
    if src_fs == dst_fs:
        return np.asarray(x, dtype=np.float32)
    if src_fs % dst_fs != 0:
        raise ValueError(f"src_fs ({src_fs}) must be a multiple of dst_fs ({dst_fs})")
    block = src_fs // dst_fs
    x = np.asarray(x, dtype=np.float32)
    n = (len(x) // block) * block
    return x[:n].reshape(-1, block).mean(axis=1)


def _label_decimate(label: np.ndarray, src_fs: int, dst_fs: int) -> np.ndarray:
    """Take the modal label within each downsampling block."""
    if src_fs == dst_fs:
        return np.asarray(label, dtype=np.int8)
    if src_fs % dst_fs != 0:
        raise ValueError(f"src_fs ({src_fs}) must be a multiple of dst_fs ({dst_fs})")
    block = src_fs // dst_fs
    n = (len(label) // block) * block
    blocks = np.asarray(label[:n]).reshape(-1, block)
    # Most-common value per row (label values are small ints in {0..7}).
    out = np.empty(blocks.shape[0], dtype=np.int8)
    for k, row in enumerate(blocks):
        vals, counts = np.unique(row, return_counts=True)
        out[k] = vals[counts.argmax()]
    return out


def load_subject(pkl_path: Path) -> WristRecord:
    """Read one ``SX.pkl`` file and return a :class:`WristRecord`."""
    with open(pkl_path, "rb") as fh:
        data = pickle.load(fh, encoding="latin1")

    wrist = data["signal"]["wrist"]
    label_raw = np.asarray(data["label"]).ravel()

    # Resample every wrist channel to TARGET_FS (4 Hz).
    acc = np.stack(
        [_decimate_to(wrist["ACC"][:, i], WRIST_FS["ACC"], TARGET_FS) for i in range(3)],
        axis=1,
    )
    bvp_4 = _decimate_to(np.asarray(wrist["BVP"]).ravel(), WRIST_FS["BVP"], TARGET_FS)
    bvp_64 = np.asarray(wrist["BVP"], dtype=np.float32).ravel()  # keep raw for HR/HRV
    eda = _decimate_to(np.asarray(wrist["EDA"]).ravel(), WRIST_FS["EDA"], TARGET_FS)
    temp = _decimate_to(np.asarray(wrist["TEMP"]).ravel(), WRIST_FS["TEMP"], TARGET_FS)

    label = _label_decimate(label_raw, LABEL_FS_RAW, TARGET_FS)

    # All wrist channels start at the same instant, but rounding can leave
    # them with slightly different lengths. Trim to the shortest.
    n = min(len(acc), len(bvp_4), len(eda), len(temp), len(label))
    rec = WristRecord(
        subject=str(data.get("subject", pkl_path.stem)),
        fs=TARGET_FS,
        acc=acc[:n].astype(np.float32),
        bvp=bvp_4[:n].astype(np.float32),
        bvp_64=bvp_64.astype(np.float32),
        eda=eda[:n].astype(np.float32),
        temp=temp[:n].astype(np.float32),
        label=label[:n],
    )
    return rec


def save_record(rec: WristRecord, out_path: Path) -> None:
    np.savez_compressed(
        out_path,
        subject=rec.subject,
        fs=rec.fs,
        acc=rec.acc,
        bvp=rec.bvp,
        bvp_64=rec.bvp_64,
        eda=rec.eda,
        temp=rec.temp,
        label=rec.label,
    )


def load_cached(npz_path: Path) -> WristRecord:
    with np.load(npz_path) as f:
        return WristRecord(
            subject=str(f["subject"]),
            fs=int(f["fs"]),
            acc=f["acc"],
            bvp=f["bvp"],
            bvp_64=f["bvp_64"],
            eda=f["eda"],
            temp=f["temp"],
            label=f["label"],
        )


def discover_subjects(wesad_root: Path) -> list[Path]:
    """Return every ``SX.pkl`` under ``WESAD/``, sorted by subject number."""
    paths = sorted(wesad_root.glob("S*/S*.pkl"),
                   key=lambda p: int(p.stem.lstrip("S")))
    return paths
