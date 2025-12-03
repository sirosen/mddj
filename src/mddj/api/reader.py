from __future__ import annotations

import collections.abc
import functools
import pathlib

import tomlkit

from .._internal import _cached_toml, _types
from .config import ReaderConfig
from .tox_reader import ToxReader

try:
    import importlib_metadata as _importlib_metadata
except ImportError:
    import importlib.metadata as _importlib_metadata


class Reader:
    """
    A Reader is an interface for data reading capabilities.

    Typically, users should simply create a DJ and then access the reader built by it,
    as in:

    .. code-block:: pycon

        >>> from mddj.api import DJ
        >>> dj = DJ()
        >>> dj.read.version()
        '0.1.0'

    :ivar tox: a :class:`ToxReader` provided by this reader
    """

    def __init__(
        self,
        config: ReaderConfig,
        document_cache: _cached_toml.TomlDocumentCache | None = None,
    ) -> None:
        self.config = config
        self._document_cache = document_cache or _cached_toml.TomlDocumentCache()

        self.tox = ToxReader()

    @functools.cached_property
    def _wheel_metadata(self) -> _importlib_metadata.PackageMetadata:
        return _get_wheel_metadata(
            self.config.project_directory,
            isolated=self.config.isolated_builds,
            quiet=self.config.capture_build_output,
        )

    @functools.cached_property
    def _pyproject_toml_document(self) -> tomlkit.TOMLDocument:
        return self._document_cache.load(self.config.pyproject_path)

    @functools.cached_property
    def _pyproject_dynamic(self) -> tuple[str, ...]:
        try:
            value = _read_pyproject_toml_value(
                self._pyproject_toml_document, "project", "dynamic"
            )
        except (FileNotFoundError, LookupError):
            return ()
        if _types.is_toml_array(value) and all(isinstance(x, str) for x in value):
            return tuple(value)
        raise LookupError("project.dynamic must be an array of strings when present")

    def _read_static(self, key: str) -> object | None:
        if key in self._pyproject_dynamic:
            return None

        try:
            return _read_pyproject_toml_value(
                self._pyproject_toml_document, "project", key
            )
        except (FileNotFoundError, LookupError):
            return None

    def _lookup(self, project_fieldname: str, metadata_fieldname: str) -> object | None:
        value = self._read_static(project_fieldname)
        if value is not None:
            return value
        return self._wheel_metadata.get(  # type: ignore[no-any-return]
            metadata_fieldname
        )

    def name(self) -> str:
        return str(self._lookup("name", "Name"))

    def version(self) -> str:
        """Get the version of the project."""
        return str(self._lookup("version", "Version"))

    def description(self) -> str:
        return str(self._lookup("description", "Summary"))

    @functools.cached_property
    def _keywords(self) -> tuple[str, ...]:
        value = self._lookup("keywords", "Keywords")
        if _types.is_toml_array(value):  # pyproject.toml it's an array
            return tuple(str(k) for k in value)
        if isinstance(value, str):  # but in metadata it's a commasep str
            return tuple(value.split(","))
        return ()

    def keywords(self) -> tuple[str, ...]:
        return self._keywords

    @functools.cached_property
    def _requires_python(self) -> str:
        value = self._lookup("requires-python", "Requires-Python")
        if value is None:
            raise LookupError("No Requires-Python data found")
        return str(value)

    def requires_python(self, *, lower_bound: bool = False) -> str:
        """
        Get the Requires-Python bound for the project.

        :param lower_bound: When true, only get the lower bound of a `>=` expression.
            Only `>=` is supported. Any other comparator will produce a ValueError if
            `lower_bound` is set.
        """
        if lower_bound:
            return _requires_python_lower_bound(self._requires_python)
        return self._requires_python

    @functools.cached_property
    def _dependencies(self) -> tuple[str, ...]:
        value: object | None = self._read_static("dependencies")

        if _types.is_toml_array(value):
            return tuple(str(d) for d in value)

        return tuple(str(d) for d in self._wheel_metadata.get_all("Requires-Dist"))

    def dependencies(self) -> tuple[str, ...]:
        """Get the dependencies for the project."""
        return self._dependencies


def _requires_python_lower_bound(req: str) -> str:
    reqs = req.split(",")
    lower_bounds = []
    for r in reqs:
        if r.startswith(">="):
            lower_bounds.append(r[2:])
        elif r.startswith(">"):
            raise ValueError(
                "Found a > requirement, rejecting as invalid (use '>=' instead)"
            )
    if len(lower_bounds) > 1:
        raise ValueError("Found multiple lower bounds, cannot choose one")
    elif len(lower_bounds) == 0:
        raise ValueError("Found no lower bounds")
    else:
        return lower_bounds[0]


def _get_wheel_metadata(
    source_dir: pathlib.Path, isolated: bool = True, quiet: bool = True
) -> _importlib_metadata.PackageMetadata:
    """
    Get metadata for wheel, either using the PEP 517 hook or by actually
    doing a wheel build and examining the result.
    """
    import build.util
    import pyproject_hooks

    runner = pyproject_hooks.quiet_subprocess_runner
    if not quiet:
        runner = pyproject_hooks.default_subprocess_runner
    return build.util.project_wheel_metadata(
        source_dir, isolated=isolated, runner=runner
    )


def _read_pyproject_toml_value(
    pyproject_data: tomlkit.TOMLDocument, *path: str | int
) -> object:
    """
    Read an arbitrary value from 'pyproject.toml'
    """
    # traverse the TOML data structure
    cursor: _types.TomlValue = pyproject_data
    for subkey in path:
        # pedantically enumerate the branches for static type checking to
        # easily see the association between key and container types
        if isinstance(subkey, str) and _types.is_toml_mapping(  # slyp: disable=W200
            cursor
        ):
            cursor = cursor[subkey]
        elif isinstance(subkey, int) and _types.is_toml_array(cursor):
            cursor = cursor[subkey]
        else:
            message = f"Could not lookup '{path}' in pyproject.toml."
            # str is a container and a scalar...
            if isinstance(cursor, str) or not isinstance(
                cursor, collections.abc.Container
            ):
                message = f"{message} Terminated in a non-container type."
            else:
                message = f"{message} Incorrect index type."
            raise LookupError(message)

    return cursor
