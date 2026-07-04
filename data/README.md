# Data policy

Raw TDMS files and Excel test logs are intentionally not stored in this repository.

Suggested local layout:

```text
data/
├── raw/          # original TDMS files and test logs, ignored by Git
├── interim/      # joined/resampled TDMS or CSV outputs, ignored by Git
├── processed/    # analysis-ready tables, ignored by Git
└── results/      # plots, summaries, reports, ignored by Git
```

Use small synthetic examples in `examples/` and `tests/` for public, reproducible demonstrations.
