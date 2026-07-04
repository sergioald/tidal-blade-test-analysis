"""Small public example that does not require private TDMS files."""

from __future__ import annotations

import numpy as np

from tidal_blade_test_analysis.static import fit_load_displacement


def main() -> None:
    displacement_mm = np.linspace(0, 12, 50)
    load_kn = 3.5 * displacement_mm + 0.2
    result = fit_load_displacement(load=load_kn, displacement=displacement_mm)
    print(result)


if __name__ == "__main__":
    main()
