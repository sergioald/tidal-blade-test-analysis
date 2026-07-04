"""TDMS input/output helpers.

The public repository does not contain raw TDMS files. These functions import
``nptdms`` only when needed, so the core numerical tests can run without data.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class ChannelSummary:
    """Compact metadata for a TDMS channel."""

    file: str
    group: str
    channel: str
    samples: int
    dtype: str
    wf_start_time: str | None = None
    wf_increment: float | None = None
    wf_start_offset: float | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def discover_tdms_files(root: str | Path) -> list[Path]:
    """Return TDMS files below ``root``, sorted for reproducibility."""
    root_path = Path(root).expanduser()
    if not root_path.exists():
        raise FileNotFoundError(f"Input folder does not exist: {root_path}")
    return sorted(p for p in root_path.rglob("*.tdms") if p.is_file())


def summarise_tdms_file(path: str | Path) -> list[ChannelSummary]:
    """Read TDMS channel metadata without loading all channels into memory."""
    from nptdms import TdmsFile  # imported lazily

    tdms_path = Path(path).expanduser()
    tdms = TdmsFile.read_metadata(tdms_path)
    rows: list[ChannelSummary] = []
    for group in tdms.groups():
        for channel in group.channels():
            props = channel.properties
            rows.append(
                ChannelSummary(
                    file=str(tdms_path),
                    group=group.name,
                    channel=channel.name,
                    samples=len(channel),
                    dtype=str(getattr(channel, "dtype", "unknown")),
                    wf_start_time=str(props.get("wf_start_time"))
                    if props.get("wf_start_time") is not None
                    else None,
                    wf_increment=float(props["wf_increment"])
                    if "wf_increment" in props
                    else None,
                    wf_start_offset=float(props["wf_start_offset"])
                    if "wf_start_offset" in props
                    else None,
                )
            )
    return rows


def summarise_tdms_tree(root: str | Path) -> pd.DataFrame:
    """Summarise every TDMS channel below a directory."""
    rows: list[dict[str, object]] = []
    for file_path in discover_tdms_files(root):
        rows.extend(row.as_dict() for row in summarise_tdms_file(file_path))
    return pd.DataFrame(rows)


def channel_to_dataframe(
    path: str | Path,
    group: str,
    channel: str,
    *,
    time_column: str = "time_s",
    value_column: str | None = None,
) -> pd.DataFrame:
    """Load one TDMS channel as a tidy DataFrame with a time axis when available."""
    from nptdms import TdmsFile  # imported lazily

    value_name = value_column or channel
    tdms = TdmsFile.read(Path(path).expanduser())
    tdms_channel = tdms[group][channel]
    values = tdms_channel[:]

    try:
        time_values = tdms_channel.time_track()
    except Exception:  # pragma: no cover - depends on TDMS metadata
        time_values = range(len(values))

    return pd.DataFrame({time_column: time_values, value_name: values})


def write_summary_csv(rows: Iterable[ChannelSummary], output_csv: str | Path) -> Path:
    """Write channel summaries to CSV and return the output path."""
    output_path = Path(output_csv).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([row.as_dict() for row in rows]).to_csv(output_path, index=False)
    return output_path
