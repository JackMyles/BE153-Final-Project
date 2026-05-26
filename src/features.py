"""Sliding-window physiological feature extraction.

A 60-second window is rolled across the wrist signals every 5 s. For
each window we compute a small set of features that the stress-detection
literature consistently finds informative:

* EDA  – tonic level (SCL), phasic-component AUC, SCR rate (peak count
  per minute on the high-pass-filtered signal), and SCR mean amplitude.
* HR   – mean / std heart rate from a simple bandpass-filtered BVP peak
  detection.
* HRV  – RMSSD, SDNN, pNN50 from inter-beat intervals derived from BVP.
* TEMP – mean and slope (linear regression) over the window.
* ACC  – mean ENMO (Euclidean norm minus one g), variance.

A window is labelled with the most-common WESAD label inside it. We
keep windows whose label is one of ``{baseline, stress, amusement,
meditation}`` for the classification task.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import signal as sps

from .load_wesad import WristRecord, WRIST_FS

# ----- Window configuration ----------------------------------------------

WINDOW_S = 60      # window length in seconds
STEP_S = 5         # window step in seconds
KEEP_LABELS = {1, 2, 3, 4}  # baseline, stress, amusement, meditation

# ----- BVP / HR / HRV helpers --------------------------------------------

def _bandpass(x: np.ndarray, fs: float, low: float, high: float, order: int = 3) -> np.ndarray:
    sos = sps.butter(order, [low, high], btype="bandpass", fs=fs, output="sos")
    return sps.sosfiltfilt(sos, x)


def _bvp_to_ibi(bvp: np.ndarray, fs: float) -> np.ndarray:
    """Detect heart-beat peaks in a BVP segment and return cleaned IBIs (s).

    Bandpass (0.8–3.0 Hz, i.e. 48–180 bpm) → prominence-based ``find_peaks``
    → robust trimming of unphysiological IBIs and successive-difference
    outliers (Malik criterion).
    """
    if len(bvp) < int(fs * 2):
        return np.array([])
    filt = _bandpass(bvp - np.mean(bvp), fs, 0.8, 3.0)
    # Use prominence + a moderate height (5th-percentile of |signal|);
    # this is far more robust to drift than a single global threshold.
    prom = np.std(filt) * 0.4
    peaks, _ = sps.find_peaks(filt, distance=int(fs * 0.4), prominence=prom)
    if len(peaks) < 4:
        return np.array([])
    ibi = np.diff(peaks) / fs
    # Physiological window 40–180 bpm = 0.33–1.5 s
    ibi = ibi[(ibi >= 0.33) & (ibi <= 1.5)]
    if len(ibi) < 3:
        return ibi
    # Malik rule: drop IBIs that change more than 20% from neighbour median.
    med = np.median(ibi)
    keep = np.abs(ibi - med) <= 0.30 * med
    ibi = ibi[keep]
    return ibi


def _hrv_features(ibi: np.ndarray) -> dict[str, float]:
    if len(ibi) < 4 or np.std(ibi) == 0:
        return {"hr_mean": np.nan, "hr_std": np.nan,
                "rmssd": np.nan, "sdnn": np.nan, "pnn50": np.nan}
    hr = 60.0 / ibi
    diff = np.diff(ibi)
    return {
        "hr_mean": float(np.mean(hr)),
        "hr_std": float(np.std(hr)),
        "rmssd": float(np.sqrt(np.mean(diff ** 2)) * 1000.0),   # ms
        "sdnn": float(np.std(ibi) * 1000.0),                    # ms
        "pnn50": float(np.mean(np.abs(diff) > 0.05) * 100.0),   # %
    }


# ----- EDA helpers --------------------------------------------------------

def _eda_decompose(eda: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Return (tonic, phasic) via a simple low-pass / high-pass split."""
    if len(eda) < int(fs * 8):
        return eda, np.zeros_like(eda)
    sos_lp = sps.butter(2, 0.05, btype="lowpass", fs=fs, output="sos")
    tonic = sps.sosfiltfilt(sos_lp, eda)
    phasic = eda - tonic
    return tonic, phasic


def _eda_features(eda: np.ndarray, fs: float) -> dict[str, float]:
    tonic, phasic = _eda_decompose(eda, fs)
    peaks, props = sps.find_peaks(phasic, height=0.01, distance=int(fs * 1.0))
    return {
        "eda_mean": float(np.mean(eda)),
        "eda_std": float(np.std(eda)),
        "scl_mean": float(np.mean(tonic)),
        "scl_slope": float(np.polyfit(np.arange(len(tonic)), tonic, 1)[0] * fs)
            if len(tonic) > 4 else 0.0,
        "scr_rate": float(len(peaks) / (len(eda) / fs / 60.0)),    # per minute
        "scr_mean_amp": float(np.mean(props["peak_heights"])) if len(peaks) else 0.0,
        "scr_auc": float(np.sum(np.clip(phasic, 0, None)) / fs),  # μS·s
    }


# ----- TEMP / ACC helpers -------------------------------------------------

def _temp_features(temp: np.ndarray, fs: float) -> dict[str, float]:
    if len(temp) < 4:
        return {"temp_mean": float(np.mean(temp)), "temp_slope": 0.0, "temp_std": float(np.std(temp))}
    slope = float(np.polyfit(np.arange(len(temp)) / fs, temp, 1)[0])  # °C per second
    return {"temp_mean": float(np.mean(temp)), "temp_slope": slope, "temp_std": float(np.std(temp))}


def _acc_features(acc: np.ndarray, fs: float) -> dict[str, float]:
    # The WESAD .pkl stores wrist ACC in units of 1/64 g; convert to g.
    a = acc / 64.0
    mag = np.linalg.norm(a, axis=1)
    enmo = np.clip(mag - 1.0, 0.0, None)   # standard actigraphy proxy
    return {
        "acc_mean": float(np.mean(mag)),
        "acc_var": float(np.var(mag)),
        "enmo": float(np.mean(enmo)),
    }


# ----- Driver -------------------------------------------------------------

@dataclass
class WindowSpec:
    win_s: int = WINDOW_S
    step_s: int = STEP_S


def extract_features(rec: WristRecord, spec: WindowSpec | None = None) -> pd.DataFrame:
    """Compute the feature table for one subject."""
    spec = spec or WindowSpec()
    fs = rec.fs  # 4 Hz (slow channels). BVP is kept at 64 Hz separately.
    bvp_fs = WRIST_FS["BVP"]

    win = spec.win_s * fs
    step = spec.step_s * fs
    win_bvp = spec.win_s * bvp_fs
    step_bvp = spec.step_s * bvp_fs

    n_windows = max(0, (len(rec.label) - win) // step + 1)
    rows = []
    for k in range(n_windows):
        s, e = k * step, k * step + win
        s_bvp, e_bvp = k * step_bvp, k * step_bvp + win_bvp
        if e_bvp > len(rec.bvp_64):
            break
        lab_win = rec.label[s:e]
        # Modal label inside the window.
        vals, counts = np.unique(lab_win, return_counts=True)
        lab = int(vals[counts.argmax()])
        if lab not in KEEP_LABELS:
            continue
        center_s = (s + e) / 2.0 / fs

        ibi = _bvp_to_ibi(rec.bvp_64[s_bvp:e_bvp], bvp_fs)
        feats = {
            "subject": rec.subject,
            "t_center_s": center_s,
            "label": lab,
            "is_stress": int(lab == 2),
        }
        feats.update(_eda_features(rec.eda[s:e], fs))
        feats.update(_hrv_features(ibi))
        feats.update(_temp_features(rec.temp[s:e], fs))
        feats.update(_acc_features(rec.acc[s:e], fs))
        rows.append(feats)

    return pd.DataFrame(rows)


FEATURE_COLUMNS = [
    "eda_mean", "eda_std", "scl_mean", "scl_slope",
    "scr_rate", "scr_mean_amp", "scr_auc",
    "hr_mean", "hr_std", "rmssd", "sdnn", "pnn50",
    "temp_mean", "temp_slope", "temp_std",
    "acc_mean", "acc_var", "enmo",
]
