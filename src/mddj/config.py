import dataclasses
import enum
import functools
import pathlib
import sys

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


_WRITE_VERSION_MODES = ("assign",)


@dataclasses.dataclass
class WriteVersionConfig:
    pass


@dataclasses.dataclass
class WriteVersionAssignConfig(WriteVersionConfig):
    path: pathlib.Path
    key: str


class ReadVersionSetting(enum.Enum):
    # the default behavior is to first try to read pyproject.toml
    # and fallback to getting build metadata if that doesn't work
    default = enum.auto()
    pyproject = enum.auto()
    build = enum.auto()


@dataclasses.dataclass
class ConfigData:
    write_version: str
    read_version: str

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

        if write_version_mode == "assign":
            if ":" in write_version_value:
                (
                    write_version_path,
                    _,
                    write_version_value,
                ) = write_version_value.partition(":")
                write_version_path = write_version_path.strip()
            else:
                write_version_path = "pyproject.toml"
            write_version_value = write_version_value.strip()

            return WriteVersionAssignConfig(
                path=pathlib.Path(write_version_path),
                key=write_version_value,
            )
        else:
            raise NotImplementedError(
                "Internal error. "
                f"Unimplemented write_version_mode: {write_version_mode}"
            )

    @functools.cached_property
    def read_version_setting(self) -> ReadVersionSetting:
        if self.read_version == "default":
            return ReadVersionSetting.default
        elif self.read_version == "pyproject.toml":
            return ReadVersionSetting.pyproject
        elif self.read_version == "build":
            return ReadVersionSetting.build
        else:
            raise ValueError("read_version must be one of ['pyproject.toml', 'build'].")


def _default_config() -> ConfigData:
    return ConfigData(
        write_version="assign: pyproject.toml: version",
        read_version="default",
    )


def read_config(pyproject_path: pathlib.Path) -> ConfigData:
    default = _default_config()
    if not pyproject_path.exists():
        return default

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    try:
        mddj_data = data["tool"]["mddj"]
    except KeyError:
        return default

    return ConfigData(
        write_version=mddj_data.get("write_version", default.write_version),
        read_version=mddj_data.get("read_version", default.read_version),
    )
