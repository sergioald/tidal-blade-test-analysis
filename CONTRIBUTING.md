# Contributing

This repository is intended to preserve the original LoadTide/FastBlade TDMS-processing scripts while gradually moving repeated operations into tested Python modules.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

## Contribution rules

1. Keep raw TDMS files, Excel logs, and derived result folders out of Git.
2. Add reusable code under `src/tidal_blade_test_analysis/` rather than adding new monolithic scripts.
3. Add tests for any new signal-processing, static-fitting, fatigue, or TDMS-summary logic.
4. Keep `legacy/` scripts for provenance, but prefer new commands through `tidal-blade-test`.
