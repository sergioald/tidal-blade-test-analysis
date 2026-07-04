# Workflow guide

## 1. Prepare a local working tree

```bash
tidal-blade-test init --root .
```

Place private files locally, not in Git:

```text
data/raw/
├── Loadtide_Test_Log.xlsx
└── <test folders or TDMS files>
```

## 2. Select a test configuration

Start from one of the public templates:

```text
examples/config.single_actuator.yml
examples/config.single_vs_multi_actuator.yml
examples/config.example.yml
```

These files document actuator positions, load direction, target root bending moment, and workflow intent.

## 3. Inventory TDMS channels

```bash
tidal-blade-test summarise data/raw --output data/results/channel_summary.csv
```

Use the inventory to check:

- expected groups and channels;
- sample counts per channel;
- waveform time increments;
- missing channels;
- files with unexpectedly short or long duration.

## 4. Run lightweight public analyses

For CSV exports or processed tables:

```bash
tidal-blade-test fft data/processed/free_decay.csv --column load --sample-rate-hz 2500
tidal-blade-test static-fit data/processed/static_case.csv --load-column load --displacement-column displacement
```

## 5. Check actuator geometry

The package includes simple point-load helpers for configuration checks:

```python
from tidal_blade_test_analysis.actuator import root_bending_moment_knm

rbm = root_bending_moment_knm(loads_kn=[95, 95, 95], positions_m=[2.26, 3.56, 4.48])
print(rbm)
```
