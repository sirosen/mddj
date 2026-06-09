import argparse
import functools
import pathlib
import shlex
import typing as t

# for some reason, mypy flags 'loads' as not explicitly exported
from ryaml import loads as _ryaml_loads  # type: ignore[attr-defined]

from ..._internal import _cached_methods, _toml_path
from ..config import ReadthedocsConfig


class ReadthedocsConfigNotFoundError(ValueError):
    pass


class ReadthedocsReader:
    """
    A ReadthedocsReader is a data reader for ``readthedocs`` configuration.

    Typically, users should simply create a DJ and then access the reader built by
    it, as in:

    .. code-block:: pycon

        >>> from mddj.api import DJ
        >>> dj = DJ()
        >>> dj.read.readthedocs.python_version()
        '3.11'
    """

    def __init__(self, config: ReadthedocsConfig) -> None:
        self._config = config
        self._method_cache: dict[t.Any, t.Any] = {}

    @functools.cached_property
    def _config_path(self) -> pathlib.Path:
        rtd_dir = self._config.dir_explorer.search_for("readthedocs").dirpath
        yaml_path = rtd_dir / ".readthedocs.yaml"
        if yaml_path.exists():
            return yaml_path
        yml_path = rtd_dir / ".readthedocs.yml"
        if yml_path.exists():
            return yml_path
        raise NotImplementedError(
            "No ReadTheDocs configuration was found, even though dir detection passed."
        )

    @_cached_methods.cached_method
    def _load_data(self) -> dict[str, t.Any]:
        content = self._config_path.read_text()

        data = _ryaml_loads(content)
        if not isinstance(data, dict):
            raise ValueError("Expected readthedocs config to parse as a dict.")
        return data

    @functools.cached_property
    def _parsed_version_path(self) -> list[str | int]:
        return _toml_path.parse_toml_path(self._config.python_version_path)

    @_cached_methods.cached_method
    def python_version(self) -> str:
        """
        Read the Python version out of ReadTheDocs configuration, using the
        configured read method.
        """
        config_body = self._load_data()
        value = config_body
        for part in self._parsed_version_path:
            # mypy flags that parts are 'int|str', but the config_body is declared as
            # a 'dict[str, Any]'
            value = value[part]  # type: ignore[index]

        if self._config.python_version_extraction == "verbatim":
            return _verbatim_process_parsed_version(value)
        elif self._config.python_version_extraction == "parse_uv_tool_install":
            return _extract_uv_tool_install_version(value)
        else:
            raise NotImplementedError(
                "configuration error: ReadthedocsReader does not support "
                f"{self._config.python_version_extraction}"
            )


def _verbatim_process_parsed_version(value: t.Any) -> str:
    # unfortunately, it could be an unquoted value, parsed as a float...
    if not isinstance(value, (str, float)):
        raise LookupError(
            "verbatim lookup of the python version from readthedocs "
            f"config got a value of an invalid type: {value!r}"
        )

    return str(value)


def _extract_uv_tool_install_version(commands: t.Any) -> str:
    if isinstance(commands, str):
        commands = [commands]
    if not isinstance(commands, list):
        raise LookupError(
            "'uv tool install' version parsing requires a path to install "
            "commands, which should be a string or list of strings."
        )
    for cmd in commands:
        if not isinstance(cmd, str):
            continue
        split_cmd = shlex.split(cmd)
        if split_cmd[:3] != ["uv", "tool", "install"]:
            continue
        break
    else:
        raise LookupError("Did not find a 'uv tool install' command.")

    parser = argparse.ArgumentParser()
    parser.add_argument("--python")
    parsed_args, _ = parser.parse_known_args(split_cmd)

    parsed_python_version: str | None = parsed_args.python
    if parsed_python_version:
        return parsed_python_version

    raise LookupError("'uv tool install' command did not specify '--python'")
