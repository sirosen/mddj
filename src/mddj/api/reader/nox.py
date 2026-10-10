from __future__ import annotations

import functools
import json
import pathlib
import shutil
import subprocess
import sys
import types
import typing as t

from ..._internal import _discovery


class NoxReaderError(RuntimeError):
    """The class of errors which can be raised if ``nox`` data discovery fails."""


class NoxReader(t.Protocol):
    """
    A NoxReader is a specialized data reader for ``nox`` data.

    Construction is private.
    Users should create a DJ and then access the nox reader built by it, as in:

    .. code-block:: pycon

        >>> from mddj.api import DJ
        >>> dj = DJ()
        >>> dj.read.nox.list_versions()
        ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13']
    """

    _dir_explorer: _discovery.DirExplorer

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        if not hasattr(self, "_dir_explorer"):
            raise TypeError("NoxReader construction was done improperly.")

    @functools.cached_property
    def _noxfile_dir(self) -> pathlib.Path:
        return self._dir_explorer.search_for("nox").dirpath

    @functools.cached_property
    def _nox_cmd(self) -> tuple[str, ...]:
        try:
            import nox  # noqa: F401
        except ImportError:
            nox_cmd = shutil.which("nox")
            if not nox_cmd:
                raise NoxReaderError(
                    "Cannot fetch nox data. A 'nox' command was not found."
                )
            return (nox_cmd,)
        else:
            return (sys.executable, "-m", "nox")

    @functools.cached_property
    def _nox_listenvs(self) -> tuple[types.MappingProxyType[str, t.Any], ...]:
        try:
            output = subprocess.check_output(
                [*self._nox_cmd, "--list", "--json"],
                text=True,
                stderr=subprocess.PIPE,
                cwd=self._noxfile_dir,
            )
            data = json.loads(output)
            return tuple(types.MappingProxyType(x) for x in data)
        except subprocess.CalledProcessError as err:
            if sys.version_info >= (3, 11):
                reader_error = NoxReaderError("nox listing failed")
                reader_error.add_note(err.stderr)
            else:
                reader_error = NoxReaderError(f"nox listing failed\n{err.stderr}")
            raise reader_error from err

    @functools.cached_property
    def _python_versions_in_envlist(self) -> tuple[str, ...]:
        versions = set()
        for env_data in self._nox_listenvs:
            if py_version := env_data.get("python"):
                versions.add(py_version)
        return tuple(sorted(versions))

    def list_python_versions(self) -> tuple[str, ...]:
        """List the Python versions which appear in the list of nox environments."""
        return self._python_versions_in_envlist

    def min_python_version(self) -> str:
        """
        Get the minimum Python version which appears in the environment list.

        Raises a ``LookupError`` if the list appears to be empty.
        """
        from packaging.version import Version

        sorted_versions = sorted(Version(v) for v in self._python_versions_in_envlist)
        if not sorted_versions:
            raise LookupError("No nox version data found.")

        return str(sorted_versions[0])


class _NoxReaderImplementation(NoxReader):
    def __init__(self, dir_explorer: _discovery.DirExplorer) -> None:
        self._dir_explorer = dir_explorer
