import dataclasses
import functools
import pathlib
import sys
import typing as t

import tomlkit

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

_WRITE_VERSION_MODES = ("assign", "toml")


WriteVersionConfig: t.TypeAlias = t.Union[
    "WriteVersionTomlConfig", "WriteVersionAssignConfig"
]


@dataclasses.dataclass
class WriteVersionTomlConfig:
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
class WriteVersionAssignConfig:
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


@dataclasses.dataclass
class ConfigData:
    write_version: str

    @functools.cached_property
    def write_version_config(self) -> WriteVersionConfig:
        write_version_mode, _, write_version_value = self.write_version.partition(":")

        if not write_version_value:
            raise ValueError("write_version must be of the form 'mode:value'.")

        if write_version_mode not in _WRITE_VERSION_MODES:
            raise ValueError(
                f"{write_version_mode} is not a valid mode for write_version. "
                f"Please choose one of {_WRITE_VERSION_MODES}"
            )

        if write_version_mode == "toml":
            return WriteVersionTomlConfig.parse(write_version_value)
        elif write_version_mode == "assign":
            return WriteVersionAssignConfig.parse(write_version_value)
        else:
            raise NotImplementedError(
                "Internal error. "
                f"Unimplemented write_version_mode: {write_version_mode}"
            )


def _default_config() -> ConfigData:
    return ConfigData(
        write_version="toml: pyproject.toml: project.version",
    )


def read_config(pyproject_path: pathlib.Path) -> ConfigData:
    default = _default_config()
    if not pyproject_path.exists():
        return default

    with pyproject_path.open("rb") as f:
        data = tomlkit.load(f)

    try:
        tool_table = data["tool"]
        if not isinstance(tool_table, tomlkit.items.Table):
            raise KeyError("'tool' was not a table")
        mddj_data = tool_table["mddj"]
        if not isinstance(mddj_data, tomlkit.items.Table):
            raise KeyError("'tool.mddj' was not a table")
    except KeyError:
        return default

    return ConfigData(
        write_version=mddj_data.get("write_version", default.write_version),
    )
