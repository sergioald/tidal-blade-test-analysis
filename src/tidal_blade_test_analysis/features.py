"""Feature engineering helpers for tidal blade structural-test signals.

The functions here are deliberately lightweight and data-agnostic. They create
cycle-level or fixed-window features that can be used for sensor QA/QC,
anomaly screening, stiffness-drift checks, and downstream machine-learning
experiments without requiring the private TDMS files to be included in Git.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd


_DEFAULT_STATS = ("mean", "std", "rms", "min", "max", "ptp", "crest_factor", "slope")


def _as_1d_float_array(values: Sequence[float] | np.ndarray, *, name: str = "signal") -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if len(arr) == 0:
        raise ValueError(f"{name} must contain at least one value")
    if not np.any(np.isfinite(arr)):
        raise ValueError(f"{name} must contain at least one finite value")
    return arr


def _safe_stat(values: np.ndarray, statistic: str) -> float:
    finite = values[np.isfinite(values)]
    if len(finite) == 0:
        return float("nan")
    if statistic == "mean":
        return float(np.mean(finite))
    if statistic == "std":
        return float(np.std(finite, ddof=0))
    if statistic == "rms":
        return float(np.sqrt(np.mean(finite**2)))
    if statistic == "min":
        return float(np.min(finite))
    if statistic == "max":
        return float(np.max(finite))
    if statistic == "ptp":
        return float(np.ptp(finite))
    if statistic == "crest_factor":
        rms = np.sqrt(np.mean(finite**2))
        if rms == 0:
            return float("nan")
        return float(np.max(np.abs(finite)) / rms)
    if statistic == "slope":
        if len(finite) < 2:
            return float("nan")
        x = np.arange(len(finite), dtype=float)
        return float(np.polyfit(x, finite, deg=1)[0])
    raise ValueError(f"Unsupported statistic: {statistic}")


def rolling_window_features(
    data: pd.DataFrame,
    signal_columns: Sequence[str],
    *,
    window_size: int,
    step_size: int | None = None,
    statistics: Sequence[str] = _DEFAULT_STATS,
    time_column: str | None = None,
) -> pd.DataFrame:
    """Create fixed-window statistical features from time-series channels.

    Parameters
    ----------
    data:
        Input table containing one or more signal columns.
    signal_columns:
        Columns to featurise.
    window_size:
        Number of samples in each window.
    step_size:
        Number of samples between consecutive windows. Defaults to
        ``window_size`` for non-overlapping windows.
    statistics:
        Statistics to compute for every signal column. Supported values are
        ``mean``, ``std``, ``rms``, ``min``, ``max``, ``ptp``,
        ``crest_factor``, and ``slope``.
    time_column:
        Optional column used to report the first, last, and centre time of each
        window.
    """
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    step = window_size if step_size is None else int(step_size)
    if step <= 0:
        raise ValueError("step_size must be positive")
    missing = [column for column in signal_columns if column not in data.columns]
    if missing:
        raise KeyError(f"Missing signal columns: {missing}")
    if time_column is not None and time_column not in data.columns:
        raise KeyError(f"Missing time column: {time_column}")
    if len(data) < window_size:
        return pd.DataFrame()

    rows: list[dict[str, float | int]] = []
    for start in range(0, len(data) - window_size + 1, step):
        stop = start + window_size
        row: dict[str, float | int] = {"window_start": start, "window_stop": stop - 1}
        if time_column is not None:
            time_values = data[time_column].iloc[start:stop].to_numpy(dtype=float)
            row["time_start"] = float(time_values[0])
            row["time_stop"] = float(time_values[-1])
            row["time_centre"] = float((time_values[0] + time_values[-1]) / 2.0)
        for column in signal_columns:
            values = data[column].iloc[start:stop].to_numpy(dtype=float)
            for statistic in statistics:
                row[f"{column}__{statistic}"] = _safe_stat(values, statistic)
        rows.append(row)
    return pd.DataFrame(rows)


def cycle_response_features(
    load: Sequence[float] | np.ndarray,
    responses: Mapping[str, Sequence[float] | np.ndarray],
    turning_point_indices: Sequence[int] | np.ndarray,
) -> pd.DataFrame:
    """Summarise load and response changes between successive turning points.

    This is useful for fatigue tests where each half-cycle can be represented by
    a load range and a response range/gradient. The function does not impose a
    rainflow convention; it simply converts ordered turning points into a tidy
    feature table suitable for QA/QC or ML screening.
    """
    load_arr = _as_1d_float_array(load, name="load")
    idx = np.asarray(turning_point_indices, dtype=int)
    if idx.ndim != 1 or len(idx) < 2:
        raise ValueError("At least two turning-point indices are required")
    if np.any(idx < 0) or np.any(idx >= len(load_arr)):
        raise IndexError("turning-point indices are outside the load array")
    if np.any(np.diff(idx) <= 0):
        raise ValueError("turning-point indices must be strictly increasing")

    response_arrays = {name: _as_1d_float_array(values, name=name) for name, values in responses.items()}
    for name, values in response_arrays.items():
        if len(values) != len(load_arr):
            raise ValueError(f"Response {name!r} must have the same length as load")

    rows: list[dict[str, float | int]] = []
    for cycle_id, (start, stop) in enumerate(zip(idx[:-1], idx[1:]), start=1):
        lo = load_arr[start : stop + 1]
        load_range = float(np.nanmax(lo) - np.nanmin(lo))
        row: dict[str, float | int] = {
            "cycle_segment": cycle_id,
            "sample_start": int(start),
            "sample_stop": int(stop),
            "n_samples": int(stop - start + 1),
            "load_min": float(np.nanmin(lo)),
            "load_max": float(np.nanmax(lo)),
            "load_range": load_range,
        }
        for name, values in response_arrays.items():
            segment = values[start : stop + 1]
            response_range = float(np.nanmax(segment) - np.nanmin(segment))
            row[f"{name}__min"] = float(np.nanmin(segment))
            row[f"{name}__max"] = float(np.nanmax(segment))
            row[f"{name}__range"] = response_range
            row[f"{name}__range_per_load_range"] = (
                response_range / load_range if load_range != 0 else float("nan")
            )
        rows.append(row)
    return pd.DataFrame(rows)
