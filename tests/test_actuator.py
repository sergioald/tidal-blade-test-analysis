import math

import pytest

from tidal_blade_test_analysis.actuator import (
    ActuatorSetup,
    equal_actuator_load_for_target_rbm,
    resolve_load_components,
    root_bending_moment_knm,
)


def test_root_bending_moment_single_actuator():
    assert root_bending_moment_knm([184.0], [3.55]) == pytest.approx(653.2)


def test_root_bending_moment_three_actuators():
    positions = [2.26, 3.56, 4.48]
    loads = [95.0, 95.0, 95.0]
    assert root_bending_moment_knm(loads, positions) == pytest.approx(978.5)


def test_equal_load_for_target_rbm():
    positions = [2.26, 3.56, 4.48]
    assert equal_actuator_load_for_target_rbm(974.7, positions) == pytest.approx(94.63, abs=0.01)


def test_resolve_load_components_matches_reported_angle():
    x_component, y_component = resolve_load_components(100.0, 14.58)
    assert x_component == pytest.approx(96.8, abs=0.1)
    assert y_component == pytest.approx(25.2, abs=0.1)


def test_actuator_setup_validates_positions():
    with pytest.raises(ValueError):
        ActuatorSetup.from_positions([0.0])


def test_actuator_setup_methods():
    setup = ActuatorSetup.from_positions([2.26, 3.56, 4.48], name="three actuator")
    assert setup.actuator_count == 3
    assert setup.root_bending_moment([65.0, 65.0, 65.0]) == pytest.approx(669.5)
    assert math.isfinite(setup.equal_load_for_target_rbm(670.0))
