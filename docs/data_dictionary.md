# Data dictionary

The public repository does not include raw TDMS or Excel data. This page documents the expected families of channels and derived outputs used by the analysis workflows.

## Input families

| Family | Examples | Typical use |
|---|---|---|
| Load cells | actuator loads, root load summaries | Static/fatigue target tracking and root bending moment checks |
| Displacement | blade centre, blade tip, actuator displacement | Load-displacement curves and stiffness indicators |
| Strain gauges | linear and rosette strain channels | Static/fatigue strain response and comparison across blade stations |
| Accelerometers | blade or frame acceleration | Natural-frequency and damping analysis |
| Time metadata | TDMS waveform start/increment, timestamps | Synchronisation, sample-count checks, and drift diagnostics |
| Test logs | test type, actuator setup, target loads, notes | Configuration and provenance |

## Derived outputs

| Output | Description |
|---|---|
| Channel inventory | One row per TDMS channel with group, name, sample count, dtype, and waveform metadata |
| FFT/natural-frequency summary | Dominant frequency peaks from free-decay or vibration signals |
| Static fit | Linear load-displacement fit metrics and residuals |
| Fatigue cycle summary | Peak/trough indices, cycle ranges, crest/trough summaries |
| Actuator/RBM summary | Point-load root bending moment and equal-load checks for actuator layouts |

## Data policy

Raw TDMS files, Excel logs, DIC images, and generated result folders should remain outside Git. Use `data/raw`, `data/interim`, `data/processed`, and `data/results` locally; these paths are ignored by default.
