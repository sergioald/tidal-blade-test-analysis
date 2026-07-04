import numpy as np
import pytest

from tidal_blade_test_analysis.static import fit_load_displacement


def test_fit_load_displacement_exact_line():
    displacement = np.array([0.0, 1.0, 2.0, 3.0])
    load = 10.0 * displacement + 2.0

    result = fit_load_displacement(load=load, displacement=displacement)

    assert result.slope == pytest.approx(10.0)
    assert result.intercept == pytest.approx(2.0)
    assert result.r2 == pytest.approx(1.0)
    assert result.rmse == pytest.approx(0.0)
    assert result.n_samples == 4


def test_fit_rejects_shape_mismatch():
    with pytest.raises(ValueError):
        fit_load_displacement(load=[1, 2, 3], displacement=[1, 2])
