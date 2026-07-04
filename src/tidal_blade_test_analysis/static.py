"""Static load-displacement analysis helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LinearFitResult:
    """Linear calibration result for load-displacement data."""

    slope: float
    intercept: float
    r2: float
    rmse: float
    n_samples: int

    def predict(self, x: np.ndarray | list[float]) -> np.ndarray:
        return self.slope * np.asarray(x, dtype=float) + self.intercept


def fit_load_displacement(load: np.ndarray | list[float], displacement: np.ndarray | list[float]) -> LinearFitResult:
    """Fit ``load = slope * displacement + intercept``.

    This captures a common static-test calculation from the legacy scripts in a
    small, testable function.
    """
    x = np.asarray(displacement, dtype=float)
    y = np.asarray(load, dtype=float)
    if x.shape != y.shape:
        raise ValueError("load and displacement must have the same shape")
    if x.ndim != 1:
        raise ValueError("load and displacement must be one-dimensional")
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    if len(x) < 2:
        raise ValueError("At least two finite samples are required")

    slope, intercept = np.polyfit(x, y, deg=1)
    pred = slope * x + intercept
    residual = y - pred
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    rmse = float(np.sqrt(np.mean(residual**2)))
    return LinearFitResult(
        slope=float(slope),
        intercept=float(intercept),
        r2=float(r2),
        rmse=rmse,
        n_samples=int(len(x)),
    )
