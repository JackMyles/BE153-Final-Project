"""Figure generation for the BE 153 final-project slides."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve

from .load_wesad import WristRecord, LABEL_NAMES, TARGET_FS
from .cortisol_sim import simulate_cortisol
from .model import ModelResult


PROTOCOL_COLOR = {
    1: "#9ecae1",  # baseline – blue
    2: "#fb6a4a",  # stress   – red
    3: "#fdd0a2",  # amusement – orange
    4: "#a1d99b",  # meditation – green
}


# ----- Helpers ------------------------------------------------------------

def _shade_protocol(ax, label: np.ndarray, fs: float) -> None:
    """Shade contiguous WESAD protocol blocks behind a time-domain trace."""
    if len(label) == 0:
        return
    t = np.arange(len(label)) / fs / 60.0  # min
    boundaries = np.flatnonzero(np.diff(label) != 0) + 1
    starts = np.concatenate([[0], boundaries])
    ends = np.concatenate([boundaries, [len(label)]])
    for s, e in zip(starts, ends):
        lab = int(label[s])
        if lab in PROTOCOL_COLOR:
            ax.axvspan(t[s], t[min(e, len(t) - 1)],
                       color=PROTOCOL_COLOR[lab], alpha=0.25,
                       label=f"_{LABEL_NAMES[lab]}")


def _legend_protocol(ax) -> None:
    handles = [plt.Rectangle((0, 0), 1, 1, color=PROTOCOL_COLOR[k], alpha=0.5)
               for k in PROTOCOL_COLOR]
    labels = [LABEL_NAMES[k] for k in PROTOCOL_COLOR]
    ax.legend(handles, labels, loc="upper right", fontsize=8, ncol=2,
              framealpha=0.9)


# ----- Figure 1 : raw signals + protocol ---------------------------------

def plot_wrist_signals(rec: WristRecord, out_path: Path) -> None:
    fs = rec.fs
    t = np.arange(len(rec.label)) / fs / 60.0

    fig, axes = plt.subplots(4, 1, figsize=(10, 7.5), sharex=True)
    panels = [
        ("EDA  (μS)", rec.eda, axes[0]),
        ("Skin TEMP (°C)", rec.temp, axes[1]),
        ("BVP (a.u.)", rec.bvp, axes[2]),
        ("ACC magnitude (g)", np.linalg.norm(rec.acc / 64.0, axis=1), axes[3]),
    ]
    for ylab, y, ax in panels:
        _shade_protocol(ax, rec.label, fs)
        ax.plot(t, y, color="black", lw=0.6)
        ax.set_ylabel(ylab)
        ax.margins(x=0)
    axes[-1].set_xlabel("Time (min)")
    _legend_protocol(axes[0])
    fig.suptitle(f"WESAD wrist signals — {rec.subject}", y=1.0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----- Figure 2 : cortisol kinetic simulation ----------------------------

def plot_cortisol_simulation(rec: WristRecord, out_path: Path) -> None:
    fs = rec.fs
    cort = simulate_cortisol(rec.label, fs, subject=rec.subject)
    t = np.arange(len(cort)) / fs / 60.0

    fig, ax = plt.subplots(figsize=(9, 3.6))
    _shade_protocol(ax, rec.label, fs)
    ax.plot(t, cort, color="#7a0177", lw=1.3, label="simulated cortisol")
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Cortisol (nmol/L)")
    ax.set_title(f"Modelled salivary cortisol response — {rec.subject}\n"
                 r"$dC/dt = -\lambda(C - C_{basal}) + k_s\,u(t)$,  "
                 r"$T_{1/2}=66$ min, peak $\approx 9\times$ basal")
    _legend_protocol(ax)
    ax.margins(x=0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----- Figure 3 : feature distributions ----------------------------------

def plot_feature_distributions(features: pd.DataFrame, out_path: Path,
                               cols: list[str] | None = None) -> None:
    cols = cols or ["eda_mean", "scr_rate", "hr_mean", "rmssd",
                    "temp_mean", "temp_slope", "cort_mean", "cort_slope"]
    cols = [c for c in cols if c in features.columns]
    n = len(cols)
    ncol = 4
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.2 * ncol, 2.6 * nrow))
    axes = np.atleast_1d(axes).ravel()
    for ax, col in zip(axes, cols):
        nonstress = features.loc[features["is_stress"] == 0, col].dropna()
        stress = features.loc[features["is_stress"] == 1, col].dropna()
        bins = np.histogram_bin_edges(
            pd.concat([nonstress, stress]).values, bins=40)
        ax.hist(nonstress, bins=bins, alpha=0.55, color="#3182bd",
                density=True, label="non-stress")
        ax.hist(stress, bins=bins, alpha=0.55, color="#e6550d",
                density=True, label="stress")
        ax.set_title(col, fontsize=10)
        ax.tick_params(labelsize=8)
    for ax in axes[len(cols):]:
        ax.axis("off")
    axes[0].legend(loc="upper right", fontsize=8)
    fig.suptitle("Stress vs. non-stress feature distributions", y=1.0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----- Figure 4 : ROC curves --------------------------------------------

def plot_roc(results: list[ModelResult], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 5.0))
    colors = ["#3182bd", "#e6550d", "#31a354"]
    for r, c in zip(results, colors):
        y_t, _, y_s = r.concat()
        fpr, tpr, _ = roc_curve(y_t, y_s)
        auroc = r.metrics()["auroc"]
        ax.plot(fpr, tpr, color=c, lw=2, label=f"{r.name} — AUROC {auroc:.3f}")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, lw=1)
    ax.set_xlabel("False-positive rate")
    ax.set_ylabel("True-positive rate")
    ax.set_title("Stress detection — leave-one-subject-out ROC")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----- Figure 5 : confusion matrices side-by-side ------------------------

def plot_confusions(results: list[ModelResult], out_path: Path) -> None:
    fig, axes = plt.subplots(1, len(results), figsize=(4.3 * len(results), 4.0))
    if len(results) == 1:
        axes = [axes]
    for ax, r in zip(axes, results):
        y_t, y_p, _ = r.concat()
        cm = confusion_matrix(y_t, y_p, normalize="true")
        im = ax.imshow(cm, cmap="Blues", vmin=0.0, vmax=1.0)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["non-stress", "stress"])
        ax.set_yticks([0, 1]); ax.set_yticklabels(["non-stress", "stress"])
        ax.set_title(r.name)
        for (i, j), v in np.ndenumerate(cm):
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color="white" if v > 0.5 else "black", fontsize=11)
        ax.set_xlabel("predicted"); ax.set_ylabel("true")
    fig.colorbar(im, ax=axes, shrink=0.7, label="row-normalised fraction")
    fig.suptitle("Confusion matrices (LOSO)", y=1.02)
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----- Figure 6 : per-subject AUROC bar chart ----------------------------

def plot_per_subject_auroc(results: list[ModelResult], out_path: Path) -> None:
    subjects = sorted({s for r in results for s in r.per_subject_auroc().keys()},
                      key=lambda s: int(str(s).lstrip("S")))
    width = 0.8 / len(results)
    fig, ax = plt.subplots(figsize=(max(8, 0.4 * len(subjects)), 4.0))
    colors = ["#3182bd", "#e6550d", "#31a354"]
    for i, (r, c) in enumerate(zip(results, colors)):
        pa = r.per_subject_auroc()
        y = [pa.get(s, np.nan) for s in subjects]
        x = np.arange(len(subjects)) + i * width
        ax.bar(x, y, width=width, color=c, label=r.name, alpha=0.9)
    ax.set_xticks(np.arange(len(subjects)) + width * (len(results) - 1) / 2)
    ax.set_xticklabels(subjects, fontsize=8)
    ax.set_ylim(0.5, 1.02)
    ax.set_ylabel("AUROC")
    ax.set_xlabel("Held-out subject")
    ax.axhline(1.0, color="grey", lw=0.5)
    ax.legend(loc="lower right", fontsize=9)
    ax.set_title("Per-subject test AUROC (LOSO)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----- Figure 7 : model-coefficient comparison ---------------------------

def plot_coefficients(results: list[ModelResult], out_path: Path) -> None:
    """Bar chart of standardised logistic-regression coefficients.

    Values are in z-score units of each feature, so they tell you "how
    much does a 1-sigma change in feature *f* move the log-odds of
    stress" — directly comparable across signals.
    """
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    width = 0.8 / len(results)
    all_feats = []
    for r in results:
        for f in r.feature_names:
            if f not in all_feats:
                all_feats.append(f)
    colors = ["#3182bd", "#e6550d", "#31a354"]
    for i, (r, c) in enumerate(zip(results, colors)):
        coef = np.mean(np.stack(r.coefs_std, axis=0), axis=0)
        values = {name: 0.0 for name in all_feats}
        for k, name in enumerate(r.feature_names):
            values[name] = float(coef[k])
        y_vals = [values[f] for f in all_feats]
        x = np.arange(len(all_feats)) + i * width
        ax.bar(x, y_vals, width=width, color=c, label=r.name, alpha=0.9)
    ax.set_xticks(np.arange(len(all_feats)) + width * (len(results) - 1) / 2)
    ax.set_xticklabels(all_feats, rotation=70, ha="right", fontsize=8)
    ax.set_ylabel(r"Standardised logistic coefficient $\beta$ (z-units)")
    ax.axhline(0, color="black", lw=0.5)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("Feature weights — change in log-odds(stress) per +1σ of feature")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
