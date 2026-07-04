import numpy as np

from tidal_blade_test_analysis.signal import (
    damping_ratio_from_log_decrement,
    dominant_frequencies,
    fft_spectrum,
    logarithmic_decrement_from_peaks,
)


def test_fft_recovers_single_tone_frequency():
    sample_rate = 100.0
    t = np.arange(0, 2, 1 / sample_rate)
    y = np.sin(2 * np.pi * 5.0 * t)

    peaks = dominant_frequencies(y, sample_rate, n_peaks=1, min_frequency_hz=1.0)

    assert len(peaks) == 1
    assert peaks[0][0] == np.float64(5.0)


def test_fft_spectrum_shapes_match():
    spectrum = fft_spectrum([0, 1, 0, -1], sample_rate_hz=4)
    assert spectrum.frequency_hz.shape == spectrum.amplitude.shape


def test_damping_ratio_from_peaks():
    delta = logarithmic_decrement_from_peaks([10, 8, 6.4])
    zeta = damping_ratio_from_log_decrement(delta)
    assert delta > 0
    assert 0 < zeta < 1
