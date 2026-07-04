"""Compatibility wrapper documenting the original script order.

The original scripts remain in ``legacy/original_code`` for provenance. This
wrapper is intentionally conservative: it prints the recommended manual order
instead of importing scripts that execute immediately and assume local folders.
"""

from __future__ import annotations

PIPELINE = [
    "legacy/original_code/Join_Data_pre.py",
    "legacy/original_code/Re_Sample_Data_pre.py",
    "legacy/original_code/Join_Fatigue.py",
    "legacy/original_code/Main_Analysis_update.py",
]


def main() -> None:
    print("Recommended legacy execution order:")
    for step, script in enumerate(PIPELINE, start=1):
        print(f"{step}. python {script}")
    print("\nPrefer the package CLI for new workflows: tidal-blade-test --help")


if __name__ == "__main__":
    main()
