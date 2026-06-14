from __future__ import annotations

import dataclasses
import os
import pathlib
import sys
import typing as t

from .._internal import _cached_toml
from .discovery import DirExplorer

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


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


PythonVersionExtraction: t.TypeAlias = t.Literal["verbatim", "parse_uv_tool_install"]


@dataclasses.dataclass
class ReadthedocsConfig:
    dir_explorer: DirExplorer
    python_version_path: str = "build.tools.python"
    python_version_extraction: PythonVersionExtraction = "verbatim"

    @classmethod
    def load_from_toml(
        cls,
        *,
        dir_explorer: DirExplorer,
        document_cache: _cached_toml.TomlDocumentCache,
    ) -> Self:
        import tomlkit

        if not dir_explorer.pyproject_path:
            return cls(dir_explorer)

        data = document_cache.load(dir_explorer.pyproject_path)

        try:
            tool_table = data["tool"]
            if not isinstance(tool_table, tomlkit.items.Table):
                raise KeyError("'tool' was not a table")
            mddj_data = tool_table["mddj"]
            if not isinstance(mddj_data, tomlkit.items.Table):
                raise KeyError("'tool.mddj' was not a table")

            readthedocs_conf = mddj_data["readthedocs"]
            if not isinstance(readthedocs_conf, tomlkit.items.Table):
                raise KeyError("'tool.mddj.readthedocs' was not a table")

            py_ver_path = "build.tools.python"
            if "python_version_path" in readthedocs_conf:
                py_ver_path = readthedocs_conf["python_version_path"]
                if not isinstance(py_ver_path, str):
                    raise ValueError(
                        "'tool.mddj.readthedocs.python_version_path' must be a string"
                    )

            py_ver_extraction: PythonVersionExtraction = "verbatim"
            if "python_version_extraction" in readthedocs_conf:
                py_ver_extraction = readthedocs_conf["python_version_extraction"]
                if py_ver_extraction not in ("verbatim", "parse_uv_tool_install"):
                    raise ValueError(
                        "'tool.mddj.readthedocs.python_version_extraction' must "
                        "be either 'verbatim' or 'parse_uv_tool_install'."
                    )
        except KeyError:
            return cls(dir_explorer)

        return cls(
            dir_explorer,
            python_version_path=py_ver_path,
            python_version_extraction=py_ver_extraction,
        )
