"""Signal-processing helpers used by natural-frequency and damping workflows."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Spectrum:
    """Single-sided FFT spectrum."""

    frequency_hz: np.ndarray
    amplitude: np.ndarray


def _as_1d_float_array(values: np.ndarray | list[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError("Expected a one-dimensional signal")
    if len(arr) < 2:
        raise ValueError("At least two samples are required")
    return arr


def fft_spectrum(values: np.ndarray | list[float], sample_rate_hz: float, *, detrend: bool = True) -> Spectrum:
    """Compute a single-sided FFT amplitude spectrum.

    Parameters
    ----------
    values:
        Signal samples.
    sample_rate_hz:
        Sampling frequency in Hz.
    detrend:
        Remove the mean before computing the spectrum.
    """
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    y = _as_1d_float_array(values)
    if detrend:
        y = y - np.nanmean(y)
    y = np.nan_to_num(y, nan=0.0)
    n = len(y)
    amplitude = np.abs(np.fft.rfft(y)) / n
    if n > 2:
        amplitude[1:-1] *= 2.0
    frequency = np.fft.rfftfreq(n, d=1.0 / sample_rate_hz)
    return Spectrum(frequency_hz=frequency, amplitude=amplitude)


def local_maxima(values: np.ndarray | list[float]) -> np.ndarray:
    """Return indices of simple local maxima."""
    arr = _as_1d_float_array(values)
    if len(arr) < 3:
        return np.array([], dtype=int)
    return np.flatnonzero((arr[1:-1] > arr[:-2]) & (arr[1:-1] >= arr[2:])) + 1


def dominant_frequencies(
    values: np.ndarray | list[float],
    sample_rate_hz: float,
    *,
    n_peaks: int = 5,
    min_frequency_hz: float = 0.0,
) -> list[tuple[float, float]]:
    """Return dominant frequencies as ``(frequency_hz, amplitude)`` pairs."""
    if n_peaks <= 0:
        raise ValueError("n_peaks must be positive")
    spectrum = fft_spectrum(values, sample_rate_hz)
    mask = spectrum.frequency_hz >= min_frequency_hz
    freq = spectrum.frequency_hz[mask]
    amp = spectrum.amplitude[mask]
    if len(freq) == 0:
        return []
    peak_idx = local_maxima(amp)
    if len(peak_idx) == 0:
        peak_idx = np.arange(len(amp))
    order = np.argsort(amp[peak_idx])[::-1][:n_peaks]
    selected = peak_idx[order]
    pairs = [(float(freq[i]), float(amp[i])) for i in selected]
    return sorted(pairs, key=lambda item: item[1], reverse=True)


def logarithmic_decrement_from_peaks(peaks: np.ndarray | list[float]) -> float:
    """Estimate damping logarithmic decrement from successive peak amplitudes.

    The function uses the first and last strictly positive absolute peaks.
    """
    p = np.abs(_as_1d_float_array(peaks))
    p = p[p > 0]
    if len(p) < 2:
        raise ValueError("At least two positive peaks are required")
    return float(np.log(p[0] / p[-1]) / (len(p) - 1))


def damping_ratio_from_log_decrement(delta: float) -> float:
    """Convert logarithmic decrement to equivalent viscous damping ratio."""
    if delta < 0:
        raise ValueError("Logarithmic decrement must be non-negative")
    return float(delta / np.sqrt((2.0 * np.pi) ** 2 + delta**2))
