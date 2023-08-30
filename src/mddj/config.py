import dataclasses
import functools
import pathlib
import sys

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


_WRITE_VERSION_MODES = ("assign",)


@dataclasses.dataclass
class ConfigData:
    version_path: str
    write_version: str

    @functools.cached_property
    def write_version_mode(self) -> str:
        val = self.write_version.partition(":")[0].strip()
        if val not in _WRITE_VERSION_MODES:
            raise ValueError(
                f"{val} is not a valid mode for write_version. "
                f"Please choose one of {_WRITE_VERSION_MODES}"
            )
        return val

    @functools.cached_property
    def write_version_value(self) -> str:
        val = self.write_version.partition(":")[2].strip()
        if val == "":
            raise ValueError("write_version must be of the form 'mode: value'.")
        return val


def _default_config() -> ConfigData:
    return ConfigData(
        version_path="pyproject.toml",
        write_version="assign: version",
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
        version_path=mddj_data.get("version_path", default.version_path),
        write_version=mddj_data.get("write_version", default.write_version),
    )
