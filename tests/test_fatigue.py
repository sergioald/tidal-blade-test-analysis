import numpy as np

from tidal_blade_test_analysis.fatigue import (
    cycle_ranges,
    peak_valley_indices,
    summarise_cycle_ranges,
)


def test_turning_points_and_ranges():
    y = np.array([0, 1, 0, -1, 0, 1, 0], dtype=float)
    idx = peak_valley_indices(y)
    ranges = cycle_ranges(y)

    assert idx.tolist() == [1, 3, 5]
    assert ranges.tolist() == [2.0, 2.0]


def test_cycle_summary():
    summary = summarise_cycle_ranges([0, 2, 0, -1, 0])
    assert summary.n_ranges == 1
    assert summary.max_range == 3.0
