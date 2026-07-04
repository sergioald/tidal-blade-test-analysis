"""Small fatigue-cycle helpers for repeated load histories."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CycleRangeSummary:
    """Summary of peak-to-valley ranges in a load history."""

    n_ranges: int
    mean_range: float
    max_range: float
    min_range: float


def _as_signal(values: np.ndarray | list[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError("Expected a one-dimensional signal")
    if len(arr) < 3:
        raise ValueError("At least three samples are required")
    return arr


def peak_valley_indices(values: np.ndarray | list[float]) -> np.ndarray:
    """Return indices of local peaks and valleys in chronological order."""
    y = _as_signal(values)
    peaks = np.flatnonzero((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:])) + 1
    valleys = np.flatnonzero((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:])) + 1
    return np.sort(np.concatenate([peaks, valleys])).astype(int)


def cycle_ranges(values: np.ndarray | list[float]) -> np.ndarray:
    """Return absolute ranges between successive turning points."""
    y = _as_signal(values)
    idx = peak_valley_indices(y)
    if len(idx) < 2:
        return np.array([], dtype=float)
    return np.abs(np.diff(y[idx]))


def summarise_cycle_ranges(values: np.ndarray | list[float]) -> CycleRangeSummary:
    """Summarise peak-to-valley ranges in a load history."""
    ranges = cycle_ranges(values)
    if len(ranges) == 0:
        return CycleRangeSummary(n_ranges=0, mean_range=float("nan"), max_range=float("nan"), min_range=float("nan"))
    return CycleRangeSummary(
        n_ranges=int(len(ranges)),
        mean_range=float(np.mean(ranges)),
        max_range=float(np.max(ranges)),
        min_range=float(np.min(ranges)),
    )
