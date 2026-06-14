from __future__ import annotations

import dataclasses
import functools
import pathlib
import sys
import typing as t

from ..._internal import _cached_toml
from ..discovery import DirExplorer

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

_WRITE_VERSION_MODES = ("assign", "toml")


@dataclasses.dataclass
class WriterConfig:
    """
    Configuration for a metadata writer.
    """

    dir_explorer: DirExplorer
    project_directory: pathlib.Path
    write_version: str = "toml: pyproject.toml: project.version"

    @classmethod
    def load_from_toml(
        cls,
        *,
        dir_explorer: DirExplorer,
        project_directory: pathlib.Path | None,
        document_cache: _cached_toml.TomlDocumentCache,
    ) -> Self:
        import tomlkit

        if project_directory is None:
            project_directory = dir_explorer.search_for("python-package").dirpath

        pyproject_path = project_directory / "pyproject.toml"

        if not pyproject_path.exists():
            return cls(dir_explorer=dir_explorer, project_directory=project_directory)

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
            return cls(dir_explorer, project_directory=project_directory)

        return cls(
            dir_explorer,
            project_directory=project_directory,
            write_version=write_version,
        )

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
