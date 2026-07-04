"""Baseline applied-AI utilities for structural-test anomaly screening.

These helpers are intentionally conservative: they support transparent feature
screening and unsupervised anomaly detection, but they do not claim structural
damage diagnosis without validation against labelled experimental evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler


@dataclass(frozen=True)
class AnomalyDetectionResult:
    """Result returned by :func:`fit_anomaly_detector`."""

    table: pd.DataFrame
    model: Pipeline
    feature_columns: tuple[str, ...]


def numeric_feature_columns(data: pd.DataFrame, *, exclude: Iterable[str] = ()) -> list[str]:
    """Return numeric feature columns suitable for ML models."""
    excluded = set(exclude)
    return [
        column
        for column in data.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(data[column])
    ]


def fit_anomaly_detector(
    features: pd.DataFrame,
    *,
    feature_columns: Iterable[str] | None = None,
    exclude_columns: Iterable[str] = ("window_start", "window_stop", "time_start", "time_stop"),
    contamination: float | str = "auto",
    random_state: int = 42,
) -> AnomalyDetectionResult:
    """Fit a robust-scaled Isolation Forest anomaly detector.

    The returned table contains two additional columns:

    ``anomaly_score``
        Higher means more normal according to scikit-learn's decision function.
    ``is_anomaly``
        Boolean flag where ``True`` means the detector marked the row as unusual.

    This is a baseline screening tool for data quality and exploratory analysis;
    do not interpret the labels as confirmed damage without engineering review.
    """
    if features.empty:
        raise ValueError("features must contain at least one row")
    columns = list(feature_columns) if feature_columns is not None else numeric_feature_columns(features, exclude=exclude_columns)
    if not columns:
        raise ValueError("No numeric feature columns available for anomaly detection")
    missing = [column for column in columns if column not in features.columns]
    if missing:
        raise KeyError(f"Missing feature columns: {missing}")
    matrix = features[columns].replace([np.inf, -np.inf], np.nan)
    if matrix.isna().all(axis=None):
        raise ValueError("Feature matrix contains no finite values")
    matrix = matrix.fillna(matrix.median(numeric_only=True)).fillna(0.0)

    model = Pipeline(
        steps=[
            ("scale", RobustScaler()),
            (
                "isolation_forest",
                IsolationForest(contamination=contamination, random_state=random_state),
            ),
        ]
    )
    model.fit(matrix)
    output = features.copy()
    output["anomaly_score"] = model.decision_function(matrix)
    output["is_anomaly"] = model.predict(matrix) == -1
    return AnomalyDetectionResult(table=output, model=model, feature_columns=tuple(columns))


def drift_zscore(reference: pd.DataFrame, candidate: pd.DataFrame, feature_columns: Iterable[str]) -> pd.Series:
    """Estimate feature drift using robust z-scores against a reference set.

    Returns one score per feature. Scores near zero indicate that the candidate
    median is close to the reference median; larger absolute values suggest a
    shift that may warrant inspection.
    """
    columns = list(feature_columns)
    if not columns:
        raise ValueError("feature_columns must not be empty")
    for column in columns:
        if column not in reference.columns or column not in candidate.columns:
            raise KeyError(f"Missing feature column: {column}")
    ref = reference[columns].replace([np.inf, -np.inf], np.nan)
    cand = candidate[columns].replace([np.inf, -np.inf], np.nan)
    ref_median = ref.median(numeric_only=True)
    mad = (ref - ref_median).abs().median(numeric_only=True).replace(0.0, np.nan)
    cand_median = cand.median(numeric_only=True)
    scores = 0.6745 * (cand_median - ref_median) / mad
    return scores.replace([np.inf, -np.inf], np.nan).fillna(0.0)
