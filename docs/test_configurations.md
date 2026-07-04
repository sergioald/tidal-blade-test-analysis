# Test configurations

The papers make clear that the meaning of each analysis depends on the test configuration. The public repository therefore uses configuration files to document actuator positions, target load quantities, and analysis intent.

## Single-actuator fatigue configuration

Used for the first full-scale FastBlade fatigue test.

```yaml
test_campaign: first_full_scale_fatigue
actuator_count: 1
actuator_positions_m: [3.55]
actuator_angle_deg_from_XB: 14.58
load_components:
  XBB_edgewise_fraction_approx: 0.97
  YBB_flapwise_fraction_approx: 0.26
target_quantity: root_bending_moment
primary_workflows:
  - static
  - fatigue
  - natural_frequency
  - strain_response
  - displacement_response
```

## Single-vs-multi-actuator configuration

Used for comparing the one-actuator and three-actuator tests.

```yaml
test_campaign: single_vs_multi_actuator
single_actuator:
  actuator_count: 1
  actuator_positions_m: [3.56]
three_actuator:
  actuator_count: 3
  actuator_positions_m: [2.26, 3.56, 4.48]
load_direction: XBB
target_quantity: root_bending_moment
primary_workflows:
  - static_comparison
  - fatigue_comparison
  - root_bending_moment
  - shear_force_context
  - strain_response
  - displacement_response
```

## Clamping/load-introduction context

This is included as related context, not as a supported reproduction workflow in this version.

```yaml
test_campaign: clamping_parameters
status_in_repository: related_context_only
actuator_count: 3
saddle_materials: [MDF, plywood]
clamping_methods: [manual_torque_wrench, hydraulic_bolt_tensioner]
requires_data_not_in_repo:
  - DIC image sets
  - clamping logs
  - saddle preload measurements
```

## Destructive/failure-testing context

This is included as related context, not as a supported reproduction workflow in this version.

```yaml
test_campaign: destructive_testing
status_in_repository: related_context_only
requires_data_not_in_repo:
  - failure-event logs
  - DIC images
  - acoustic-emission data
  - post-damage inspection data
  - residual-strength test outputs
```

## Why this matters

A root bending moment of the same magnitude can be produced by different actuator layouts. The downstream strain, displacement, shear-force distribution, local saddle effects, and control-system behaviour can therefore differ even when the target root bending moment is similar. Keeping these parameters in configuration files prevents the analysis scripts from hiding key experimental assumptions.
