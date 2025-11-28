from __future__ import annotations

import dataclasses
import functools
import os
import pathlib
import sys
import typing as t

from .._internal import _cached_toml

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

_WRITE_VERSION_MODES = ("assign", "toml")


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

    #: The starting directory for project dir discovery. Defaults to cwd.
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

    project_directory: pathlib.Path
    pyproject_path: pathlib.Path
    isolated_builds: bool
    capture_build_output: bool


@dataclasses.dataclass
class WriterConfig:
    """
    Configuration for a metadata writer.
    """

    project_directory: pathlib.Path
    write_version: str = "toml: pyproject.toml: project.version"

    @classmethod
    def load_from_toml(
        cls,
        *,
        project_directory: pathlib.Path,
        pyproject_path: pathlib.Path,
        document_cache: _cached_toml.TomlDocumentCache,
    ) -> Self:
        import tomlkit

        if not pyproject_path.exists():
            return cls(project_directory=project_directory)

        data = document_cache.load(pyproject_path)

        try:
            tool_table = data["tool"]
            if not isinstance(tool_table, tomlkit.items.Table):
                raise KeyError("'tool' was not a table")
            mddj_data = tool_table["mddj"]
            if not isinstance(mddj_data, tomlkit.items.Table):
                raise KeyError("'tool.mddj' was not a table")

            write_version = mddj_data["write_version"]
            if not isinstance(write_version, str):
                raise KeyError("'tool.mddj.write_version' must be a str")
        except KeyError:
            return cls(project_directory=project_directory)

        return cls(project_directory=project_directory, write_version=write_version)

    @functools.cached_property
    def write_version_settings(self) -> WriteVersionSettings:
        write_version_mode, _, write_version_value = self.write_version.partition(":")

        if not write_version_value:
            raise ValueError("write_version must be of the form 'mode:value'.")

        if write_version_mode not in _WRITE_VERSION_MODES:
            raise ValueError(
                f"{write_version_mode} is not a valid mode for write_version. "
                f"Please choose one of {_WRITE_VERSION_MODES}"
            )

        if write_version_mode == "toml":
            return WriteVersionTomlSettings.parse(write_version_value)
        elif write_version_mode == "assign":
            return WriteVersionAssignSettings.parse(write_version_value)
        else:
            raise NotImplementedError(
                "Internal error. "
                f"Unimplemented write_version_mode: {write_version_mode}"
            )


WriteVersionSettings: t.TypeAlias = t.Union[
    "WriteVersionTomlSettings", "WriteVersionAssignSettings"
]


@dataclasses.dataclass
class WriteVersionTomlSettings:
    file_path: pathlib.Path
    toml_path: str

    @classmethod
    def parse(cls, config_str: str) -> Self:
        if ":" in config_str:
            file_path, _, toml_path = config_str.partition(":")
            file_path = file_path.strip()
            toml_path = toml_path.strip()
        else:
            file_path = "pyproject.toml"
            toml_path = config_str.strip()

        return cls(file_path=pathlib.Path(file_path), toml_path=toml_path)


@dataclasses.dataclass
class WriteVersionAssignSettings:
    file_path: pathlib.Path
    key: str

    @classmethod
    def parse(cls, config_str: str) -> Self:
        if ":" in config_str:
            file_path, _, key = config_str.partition(":")
            file_path = file_path.strip()
            key = key.strip()
        else:
            file_path = "pyproject.toml"
            key = config_str.strip()

        return cls(file_path=pathlib.Path(file_path), key=key)
