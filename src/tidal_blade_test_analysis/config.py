"""Repository path conventions for TDMS processing projects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Common folder layout used by the original LoadTide processing scripts.

    Parameters
    ----------
    root:
        Project or experiment root directory. Raw data and generated outputs are
        expected below this directory, but they are ignored by Git by default.
    """

    root: Path

    @classmethod
    def from_root(cls, root: str | Path = ".") -> "ProjectPaths":
        return cls(Path(root).expanduser().resolve())

    @property
    def raw(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def interim(self) -> Path:
        return self.root / "data" / "interim"

    @property
    def processed(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def results(self) -> Path:
        return self.root / "data" / "results"

    def make_dirs(self) -> None:
        """Create the standard local data directories."""
        for path in (self.raw, self.interim, self.processed, self.results):
            path.mkdir(parents=True, exist_ok=True)
