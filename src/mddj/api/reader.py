from __future__ import annotations

import functools

import tomlkit

from .._internal import _cached_toml, _compat, _readers, _types
from .config import ReaderConfig


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
    """

    def __init__(
        self,
        config: ReaderConfig,
        document_cache: _cached_toml.TomlDocumentCache | None = None,
    ) -> None:
        self.config = config
        self._document_cache = document_cache or _cached_toml.TomlDocumentCache()

    @functools.cached_property
    def _wheel_metadata(self) -> _compat.metadata.PackageMetadata:
        return _readers.get_wheel_metadata(
            self.config.project_directory,
            isolated=self.config.isolated_builds,
            quiet=self.config.capture_build_output,
        )

    @functools.cached_property
    def _pyproject_toml_document(self) -> tomlkit.TOMLDocument:
        return self._document_cache.load(self.config.pyproject_path)

    @functools.cached_property
    def _version(self) -> str:
        try:
            return str(
                _readers.read_pyproject_toml_value(
                    self._pyproject_toml_document, "project", "version"
                )
            )
        except (FileNotFoundError, LookupError):
            return str(self._wheel_metadata.get("Version"))

    def version(self) -> str:
        """Get the version of the project."""
        return self._version

    @functools.cached_property
    def _requires_python(self) -> str:
        # first, try reading from pyproject.toml
        try:
            return str(
                _readers.read_pyproject_toml_value(
                    self._pyproject_toml_document, "project", "requires-python"
                )
            )
        except (FileNotFoundError, LookupError):
            pass

        # if that fails, fallback to trying to read from build metadata
        value = self._wheel_metadata.get("Requires-Python")
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
        try:
            value = _readers.read_pyproject_toml_value(
                self._pyproject_toml_document, "project", "dependencies"
            )
        except (FileNotFoundError, LookupError):
            value = None
        if _types.is_toml_array(value):
            return tuple(str(d) for d in value)

        return tuple(str(d) for d in self._wheel_metadata.get_all("Requires-Dist"))

    def dependencies(self) -> tuple[str, ...]:
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
