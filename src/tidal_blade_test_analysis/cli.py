"""Command-line interface for repository-level TDMS workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import ProjectPaths
from .io import summarise_tdms_file, summarise_tdms_tree, write_summary_csv
from .signal import dominant_frequencies
from .static import fit_load_displacement


def _cmd_init(args: argparse.Namespace) -> int:
    paths = ProjectPaths.from_root(args.root)
    paths.make_dirs()
    print(f"Created local data folders under {paths.root / 'data'}")
    return 0


def _cmd_summarise(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser()
    if input_path.is_file():
        rows = summarise_tdms_file(input_path)
        if args.output:
            out = write_summary_csv(rows, args.output)
            print(f"Wrote {out}")
        else:
            print(json.dumps([row.as_dict() for row in rows], indent=2))
    else:
        df = summarise_tdms_tree(input_path)
        if args.output:
            out = Path(args.output).expanduser()
            out.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(out, index=False)
            print(f"Wrote {out}")
        else:
            print(df.to_string(index=False))
    return 0


def _cmd_fft(args: argparse.Namespace) -> int:
    df = pd.read_csv(args.csv)
    peaks = dominant_frequencies(
        df[args.column].to_numpy(),
        args.sample_rate_hz,
        n_peaks=args.n_peaks,
        min_frequency_hz=args.min_frequency_hz,
    )
    for frequency, amplitude in peaks:
        print(f"{frequency:.6g} Hz,{amplitude:.6g}")
    return 0


def _cmd_static_fit(args: argparse.Namespace) -> int:
    df = pd.read_csv(args.csv)
    result = fit_load_displacement(
        load=df[args.load_column].to_numpy(),
        displacement=df[args.displacement_column].to_numpy(),
    )
    print(json.dumps(result.__dict__, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tidal-blade-test",
        description="TDMS processing utilities for tidal blade structural test data.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create local data folders ignored by Git")
    p_init.add_argument("--root", default=".")
    p_init.set_defaults(func=_cmd_init)

    p_sum = sub.add_parser("summarise", help="Summarise TDMS groups/channels")
    p_sum.add_argument("input", help="TDMS file or folder containing TDMS files")
    p_sum.add_argument("--output", "-o", help="Optional CSV output path")
    p_sum.set_defaults(func=_cmd_summarise)

    p_fft = sub.add_parser("fft", help="Find dominant frequencies from a CSV signal column")
    p_fft.add_argument("csv", help="CSV file with the signal column")
    p_fft.add_argument("--column", required=True, help="Signal column name")
    p_fft.add_argument("--sample-rate-hz", type=float, required=True)
    p_fft.add_argument("--n-peaks", type=int, default=5)
    p_fft.add_argument("--min-frequency-hz", type=float, default=0.0)
    p_fft.set_defaults(func=_cmd_fft)

    p_static = sub.add_parser("static-fit", help="Fit load = slope * displacement + intercept")
    p_static.add_argument("csv", help="CSV with load/displacement columns")
    p_static.add_argument("--load-column", default="load")
    p_static.add_argument("--displacement-column", default="displacement")
    p_static.set_defaults(func=_cmd_static_fit)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
