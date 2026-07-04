# Legacy script inventory

The original uploaded scripts are preserved under `legacy/original_code/`. Files from `Code3.zip` that differed from the fuller `Code.zip` archive are stored under `legacy/code3_alternatives/`.

## Main workflows identified

| Legacy file | Main purpose | Repository action |
|---|---|---|
| `Join_Data_pre.py` | Join/copy TDMS files from raw test folders into joined data folders | Refactor into a configurable TDMS join command |
| `Join_Post.py` | Post-join TDMS handling | Merge with the join workflow after validation |
| `Re_Sample_Data_pre.py`, `Re_Sample_Data_pre_2.py` | Resampling joined TDMS data | Refactor into a `resample` module/CLI command |
| `Join_Fatigue.py` | Fatigue-specific data preparation | Refactor after channel naming is documented |
| `Main_Analysis.py`, `Main_Analysis_LAG.py`, `Main_Analysis_update*.py` | Natural-frequency, static, and fatigue analysis variants | Replace with a single configurable analysis pipeline |
| `Fatigue Analysis.py` | Fatigue post-processing and regression | Move peak/range logic into tested functions |
| `Damping.py` | Damping analysis from free-decay/natural-frequency tests | Move logarithmic decrement logic into `signal.py` |
| `Plot_LoadvsDisp.py` | Load-displacement plotting | Convert to CLI/report plot function |
| `stat_rio.py` | Compare RIO and STC channels | Convert to synchronization/QA utility |
| `Peack_f.py` | Peak-frequency exploratory script | Replace with `tidal-blade-test fft` |
| `Chk Fatigue.py` | Fatigue data checks | Convert to QA checks |
| `Stat.py` | Static summary plotting with hard-coded values | Replace with example/report plotting |

## Issues found during repository conversion

- Several scripts execute immediately at import time.
- Multiple filenames contain spaces, which makes CLI use and imports awkward.
- Some scripts contain hard-coded Windows/OneDrive paths.
- Several analysis versions appear to be incremental variants rather than separate maintained modules.
- Raw TDMS and Excel data are assumed but not included.
- No original tests were present in the uploaded archives.

## Current repository decision

The repository keeps legacy files intact for provenance and adds a modern package layer for reusable, testable logic. This avoids breaking the original workflow before the private TDMS archive is available for regression testing.
