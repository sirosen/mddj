from __future__ import annotations

import functools
import pathlib

from .._internal import _cached_toml, _discovery
from .config import DJConfig, ReaderConfig, WriterConfig
from .reader import Reader
from .writer import Writer


class DJ:
    """
    An MDDJ DJ object is the top level access point for the library API.

    It provides programmatic access to the capabilities of MDDJ.

    Note that DJs and their components aggressively cache data so that it can be read
    many times quickly. In order to refresh state, instantiate a new DJ.
    """

    def __init__(self, config: DJConfig | None = None) -> None:
        self.config = config or DJConfig()
        self._document_cache = _cached_toml.TomlDocumentCache()

    @functools.cached_property
    def project_directory(self) -> pathlib.Path:
        """
        The directory where project metadata can be found.

        By default, this is automatically discovered on first access, but it can also be
        explicitly set via config.
        """
        if self.config.project_dir is not None:
            return self.config.project_dir

        return _discovery.discover_project_dir(self.config.discovery_start_dir)

    @functools.cached_property
    def pyproject_path(self) -> pathlib.Path:
        """
        The path to the pyproject.toml file which will be used to read and write
        metadata. The file may not actually exist, and this will not raise errors.
        """
        return self.project_directory / "pyproject.toml"

    @functools.cached_property
    def read(self) -> Reader:
        """A Reader configured via this DJ."""
        config = ReaderConfig(
            project_directory=self.project_directory,
            pyproject_path=self.pyproject_path,
            isolated_builds=self.config.isolated_builds,
            capture_build_output=self.config.capture_build_output,
        )
        return Reader(config, document_cache=self._document_cache)

    @functools.cached_property
    def write(self) -> Writer:
        """A Writer configured via this DJ."""
        config = WriterConfig.load_from_toml(self.pyproject_path)
        return Writer(config, document_cache=self._document_cache)
