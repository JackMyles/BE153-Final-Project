"""Kinetic simulation of salivary / sweat cortisol from the WESAD labels.

The HPA axis releases cortisol with a delay of ~10–20 min after a
stressor, and free cortisol is cleared from the bloodstream with an
elimination half-life of ~60–90 min. We model the concentration of
free cortisol (units: nmol/L, similar to salivary cortisol) with a
single-compartment first-order kinetic equation

    dC/dt  =  -λ ( C - C_basal )  +  k_s · u(t)                (1)

* ``u(t)`` – the HPA "drive" input. Whenever the subject is in the
  WESAD ``stress`` (TSST) condition we set ``u = 1``, else 0. A small
  amount of low-pass filtering models the ~10 min delay between
  pituitary ACTH release and adrenal cortisol secretion.
* ``λ = ln 2 / T½`` with ``T½ = 66 min``  (Czeisler & Klerman, 1999;
  Federenko et al. 2004).
* ``k_s`` is calibrated so that prolonged stress drives C up to
  ``~9 × C_basal``, matching the ~9× rise observed during academic exam
  stress in Cay et al. 2018 (NCI).
* Inter-subject variability in basal level and gain is sampled from
  log-normal distributions whose CVs come from Hellhammer et al. 2007.
* Sensor noise (CV ≈ 8 %) is added on top to mimic a wearable
  electrochemical cortisol sensor (Parlak et al. 2018; 2021).

Returns a continuous cortisol trace at the same sampling rate as the
input label vector, plus per-window summary features that the
augmented classifier consumes.
"""
from __future__ import annotations

import numpy as np

# ----- Defaults from the literature --------------------------------------

DEFAULTS = dict(
    C_basal_mean=5.0,        # nmol/L  (sweat free cortisol baseline)
    C_basal_cv=0.35,         # log-normal CV across subjects
    peak_ratio_mean=9.0,     # peak / basal during sustained stress (Cay 2018)
    peak_ratio_cv=0.40,
    half_life_min=66.0,      # cortisol elimination t1/2 (whole-body)
    # Sweat-cortisol responds faster than salivary because local sweat-gland
    # transport dominates over systemic HPA dynamics; Parlak 2018 / 2021
    # report wearable-sensor responses on the order of a few minutes.
    drive_delay_min=3.0,
    sensor_cv=0.08,          # ~8% measurement noise (Parlak 2018)
    sensor_lod=0.5,          # nmol/L practical limit of detection
)


def _smooth_drive(u: np.ndarray, fs: float, delay_min: float) -> np.ndarray:
    """One-pole low-pass that gives a smooth ACTH/cortisol rising edge."""
    tau = delay_min * 60.0  # seconds
    alpha = 1.0 / (1.0 + tau * fs)
    y = np.empty_like(u, dtype=np.float32)
    s = 0.0
    for k in range(len(u)):
        s = s + alpha * (u[k] - s)
        y[k] = s
    return y


def simulate_cortisol(
    label: np.ndarray,
    fs: float,
    subject: str | int = "S0",
    rng: np.random.Generator | None = None,
    params: dict | None = None,
) -> np.ndarray:
    """Simulate a cortisol trace given a WESAD label vector.

    Parameters
    ----------
    label : (N,) ints, the WESAD label at ``fs`` Hz
    fs    : sampling rate of ``label``
    subject : seeds the per-subject random draws so the same subject
              always gets the same kinetic constants
    rng   : optional NumPy generator (otherwise per-subject seeded)
    params : optional overrides for ``DEFAULTS``
    """
    p = {**DEFAULTS, **(params or {})}

    # Per-subject random draws (reproducible).
    if rng is None:
        seed = abs(hash(("cortisol", str(subject)))) % (2 ** 32)
        rng = np.random.default_rng(seed)
    sigma_basal = np.sqrt(np.log(1.0 + p["C_basal_cv"] ** 2))
    sigma_peak = np.sqrt(np.log(1.0 + p["peak_ratio_cv"] ** 2))
    C_basal = float(rng.lognormal(np.log(p["C_basal_mean"]) - 0.5 * sigma_basal ** 2,
                                  sigma_basal))
    peak_ratio = float(rng.lognormal(np.log(p["peak_ratio_mean"]) - 0.5 * sigma_peak ** 2,
                                     sigma_peak))

    # Solve (1) implicitly. dt small (<<1/λ) so explicit Euler is safe.
    drive = (np.asarray(label) == 2).astype(np.float32)
    drive = _smooth_drive(drive, fs, p["drive_delay_min"])
    lam = np.log(2.0) / (p["half_life_min"] * 60.0)  # 1/s

    # k_s chosen so that steady-state C from u=1 reaches peak_ratio * C_basal.
    # Steady state of (1) when u=1: C_ss = C_basal + k_s/λ. Set k_s = λ * (peak_ratio-1) * C_basal.
    k_s = lam * (peak_ratio - 1.0) * C_basal

    dt = 1.0 / fs
    C = np.empty_like(drive)
    C[0] = C_basal
    for k in range(1, len(drive)):
        C[k] = C[k - 1] + dt * (-lam * (C[k - 1] - C_basal) + k_s * drive[k - 1])

    # Add sensor noise (multiplicative, CV ≈ sensor_cv) and a soft floor at LOD.
    noise = rng.normal(loc=1.0, scale=p["sensor_cv"], size=len(C)).astype(np.float32)
    C_meas = C * noise
    C_meas = np.maximum(C_meas, p["sensor_lod"])
    return C_meas


def window_cortisol_features(
    cortisol: np.ndarray,
    fs: float,
    centers_s: np.ndarray,
    win_s: int = 60,
) -> np.ndarray:
    """Per-window summary of the simulated cortisol trace.

    Returns an (N_windows, 3) array of (mean, slope_nM_per_min, AUC).
    These are exactly the features a real intermittent / continuous
    cortisol biosensor would expose to a downstream classifier.
    """
    half = int(win_s * fs / 2)
    out = np.zeros((len(centers_s), 3), dtype=np.float32)
    for i, t_c in enumerate(centers_s):
        c_idx = int(round(t_c * fs))
        s = max(c_idx - half, 0)
        e = min(c_idx + half, len(cortisol))
        seg = cortisol[s:e]
        if len(seg) < 2:
            out[i] = [float(np.mean(seg)) if len(seg) else 0.0, 0.0, 0.0]
            continue
        t = np.arange(len(seg)) / fs / 60.0  # min
        slope = float(np.polyfit(t, seg, 1)[0])
        out[i] = [float(np.mean(seg)), slope, float(np.trapezoid(seg, t))]
    return out


CORTISOL_FEATURE_NAMES = ["cort_mean", "cort_slope", "cort_auc"]
