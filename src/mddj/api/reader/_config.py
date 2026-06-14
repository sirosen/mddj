from __future__ import annotations

import dataclasses
import pathlib

from ..discovery import DirExplorer


@dataclasses.dataclass
class ReaderConfig:
    """
    Configuration for a metadata reader.
    """

    dir_explorer: DirExplorer
    project_directory: pathlib.Path | None
    isolated_builds: bool
    capture_build_output: bool
