"""Stress-detection models.

Two linear (logistic-regression) classifiers are fit:

* **Baseline** – uses only the wrist-wearable physiological features
  (EDA, HR / HRV, TEMP, ACC), the same channels every off-the-shelf
  wearable (Empatica E4, Fitbit Sense, Apple Watch, etc.) already
  expose.
* **Augmented** – adds three cortisol features (mean, slope, AUC over
  the same 60-s window) that a next-gen electrochemical sweat-cortisol
  sensor would provide.

Both models are evaluated with **leave-one-subject-out** cross-validation
so reported metrics generalise across people, not just across windows
of the same person.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.preprocessing import StandardScaler

from .features import FEATURE_COLUMNS
from .cortisol_sim import CORTISOL_FEATURE_NAMES


@dataclass
class FoldResult:
    subject: str
    y_true: np.ndarray
    y_prob: np.ndarray
    y_pred: np.ndarray


@dataclass
class ModelResult:
    name: str
    feature_names: list[str]
    folds: list[FoldResult] = field(default_factory=list)
    coefs: list[np.ndarray] = field(default_factory=list)         # original-scale β
    coefs_std: list[np.ndarray] = field(default_factory=list)     # standardised β
    intercepts: list[float] = field(default_factory=list)

    def concat(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        y_t = np.concatenate([f.y_true for f in self.folds])
        y_p = np.concatenate([f.y_pred for f in self.folds])
        y_s = np.concatenate([f.y_prob for f in self.folds])
        return y_t, y_p, y_s

    def metrics(self) -> dict[str, float]:
        y_t, y_p, y_s = self.concat()
        return {
            "accuracy": float(accuracy_score(y_t, y_p)),
            "f1": float(f1_score(y_t, y_p)),
            "precision": float(precision_score(y_t, y_p, zero_division=0)),
            "recall": float(recall_score(y_t, y_p)),
            "auroc": float(roc_auc_score(y_t, y_s)),
            "n_pos": int(y_t.sum()),
            "n_total": int(len(y_t)),
        }

    def per_subject_auroc(self) -> dict[str, float]:
        d = {}
        for f in self.folds:
            try:
                d[f.subject] = float(roc_auc_score(f.y_true, f.y_prob))
            except ValueError:
                d[f.subject] = float("nan")
        return d


def _impute_inplace(df: pd.DataFrame, cols: list[str]) -> None:
    """Median-impute and infinity-clean numerical columns."""
    for c in cols:
        x = df[c].replace([np.inf, -np.inf], np.nan)
        df[c] = x.fillna(x.median())


def fit_loso(
    df: pd.DataFrame,
    feature_names: list[str],
    name: str,
    C: float = 1.0,
) -> ModelResult:
    """Leave-one-subject-out logistic-regression fit + evaluation.

    Parameters
    ----------
    df : feature table with columns 'subject', 'is_stress', and ``feature_names``
    feature_names : columns to use as predictors
    name : friendly model name (e.g. "baseline")
    C : inverse L2 regularisation strength
    """
    df = df.copy()
    _impute_inplace(df, feature_names)

    subjects = sorted(df["subject"].unique())
    result = ModelResult(name=name, feature_names=feature_names)

    for s in subjects:
        train = df[df["subject"] != s]
        test = df[df["subject"] == s]
        if test.empty or train["is_stress"].nunique() < 2 or test["is_stress"].nunique() < 1:
            continue

        scaler = StandardScaler().fit(train[feature_names].values)
        Xtr = scaler.transform(train[feature_names].values)
        Xte = scaler.transform(test[feature_names].values)
        ytr = train["is_stress"].values.astype(int)
        yte = test["is_stress"].values.astype(int)

        clf = LogisticRegression(
            C=C,
            max_iter=2000,
            class_weight="balanced",
            solver="liblinear",
        ).fit(Xtr, ytr)

        prob = clf.predict_proba(Xte)[:, 1]
        pred = (prob >= 0.5).astype(int)
        result.folds.append(FoldResult(subject=s, y_true=yte, y_prob=prob, y_pred=pred))
        # Standardised coefficients = ones the LR saw directly. Comparable across features.
        result.coefs_std.append(clf.coef_.ravel())
        # Original-space coefficients: β_orig_k = β_scaled_k / σ_k.
        sigma = scaler.scale_
        result.coefs.append(clf.coef_.ravel() / sigma)
        result.intercepts.append(float(clf.intercept_[0]
                                       - np.sum(clf.coef_.ravel() * scaler.mean_ / sigma)))
    return result


def average_coefficients(result: ModelResult, standardised: bool = True) -> pd.Series:
    arr = result.coefs_std if standardised else result.coefs
    coef = np.mean(np.stack(arr, axis=0), axis=0)
    return pd.Series(coef, index=result.feature_names).sort_values(key=np.abs, ascending=False)


def baseline_features() -> list[str]:
    return list(FEATURE_COLUMNS)


def augmented_features() -> list[str]:
    return list(FEATURE_COLUMNS) + list(CORTISOL_FEATURE_NAMES)
