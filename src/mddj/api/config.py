from __future__ import annotations

import dataclasses
import os
import pathlib
import typing as t

from .discovery import DirExplorer


def _bool_env_var_default_factory(varname: str, default: bool) -> t.Callable[[], bool]:
    def factory() -> bool:
        if (var := os.environ.get(varname)) is not None:
            return var.lower() not in ("0", "false")
        return default

    return factory


@dataclasses.dataclass
class DJConfig:
    """
    Configuration for a DJ object.

    Some values support having their defaults set via environment variables:

    - ``isolated_builds``: ``MDDJ_ISOLATED_BUILDS``
    - ``capture_build_output``: ``MDDJ_CAPTURE_BUILD_OUTPUT``
    """

    #: The starting directory for discovery. Defaults to cwd.
    discovery_start_dir: pathlib.Path = dataclasses.field(
        default_factory=pathlib.Path.cwd
    )
    #: The project directory. By default, it is discovered from the start directory.
    project_dir: pathlib.Path | None = None
    #: Whether or not to use isolated builds when getting metadata from build backends.
    #: Defaults to True.
    isolated_builds: bool = dataclasses.field(
        default_factory=_bool_env_var_default_factory("MDDJ_ISOLATED_BUILDS", True)
    )
    #: Whether or not to use "quiet mode" for builds when they are invoked.
    #: Defaults to True.
    capture_build_output: bool = dataclasses.field(
        default_factory=_bool_env_var_default_factory("MDDJ_CAPTURE_BUILD_OUTPUT", True)
    )


@dataclasses.dataclass
class ReaderConfig:
    """
    Configuration for a metadata reader.
    """

    dir_explorer: DirExplorer
    project_directory: pathlib.Path | None
    isolated_builds: bool
    capture_build_output: bool
