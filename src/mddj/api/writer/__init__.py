from __future__ import annotations

import functools
import pathlib
import typing as t

from ..._internal import _cached_toml, _writers
from . import _config


class Writer(t.Protocol):
    """
    A Writer is an interface for data writing capabilities.

    Construction is private.
    Users should create a DJ and then access the writer built by it, as in:

    .. code-block:: pycon

        >>> from mddj.api import DJ
        >>> dj = DJ()
        >>> dj.write.version("0.2.0")
        '0.1.0'
    """

    # attributes provided via the private "implementation" class
    _config: _config.WriterConfig
    _document_cache: _cached_toml.TomlDocumentCache

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        if not hasattr(self, "_config"):
            raise TypeError("Writer construction was done improperly.")

    @functools.cached_property
    def _python_project_directory(self) -> pathlib.Path:
        """
        The python project directory is defined as the dir with a pyproject.toml file,
        or python package root.
        """
        try:
            return self._config.dir_explorer.search_for("pyproject").dirpath
        except LookupError:
            return self._config.dir_explorer.search_for("python-package").dirpath

    @property
    def write_version_config(self) -> str:
        """The configuration (as a string) for where and how to write the version."""
        return self._config.write_version

    def version(self, new_version: str) -> str:
        """
        Write a new version into the project metadata, returning the old version.

        If no previous version can be found, a ``LookupError`` is raised, on the
        presumption that this means that the writer is not correctly configured for
        the project.
        """
        write_version_settings = self._config.write_version_settings
        file_path = self._python_project_directory / write_version_settings.file_path

        if isinstance(write_version_settings, _config.WriteVersionAssignSettings):
            result = _writers.write_simple_assignment(
                file_path, write_version_settings.key, new_version
            )
        elif isinstance(write_version_settings, _config.WriteVersionTomlSettings):
            return _writers.write_toml_value(
                file_path,
                write_version_settings.toml_path,
                new_version,
                loaded_document=self._document_cache.load(file_path),
            )
        else:
            raise NotImplementedError(
                "Unrecognized write_version_config. "
                f"write_version={self._config.write_version}"
            )

        if result is None:
            raise LookupError(
                "No previous version was found, so no update was written."
            )

        return result


class _WriterImplementation(Writer):
    _Config: t.ClassVar[type[_config.WriterConfig]] = _config.WriterConfig

    def __init__(
        self,
        config: _config.WriterConfig,
        document_cache: _cached_toml.TomlDocumentCache,
    ) -> None:
        self._config = config
        self._document_cache = document_cache
