from __future__ import annotations

import functools

from .._internal import _cached_toml
from .config import DJConfig, ReaderConfig
from .discovery import DirExplorer
from .reader import Reader, _ReaderImplementation
from .writer import Writer
from .writer import _config as _writer_config
from .writer import _WriterImplementation


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
    def dir_explorer(self) -> DirExplorer:
        return DirExplorer(
            self.config.discovery_start_dir, document_cache=self._document_cache
        )

    @functools.cached_property
    def read(self) -> Reader:
        """A Reader configured via this DJ."""
        config = ReaderConfig(
            dir_explorer=self.dir_explorer,
            project_directory=self.config.project_dir,
            isolated_builds=self.config.isolated_builds,
            capture_build_output=self.config.capture_build_output,
        )
        return _ReaderImplementation(config, document_cache=self._document_cache)

    @functools.cached_property
    def write(self) -> Writer:
        """A Writer configured via this DJ."""
        config = _writer_config.WriterConfig.load_from_toml(
            dir_explorer=self.dir_explorer,
            project_directory=self.config.project_dir,
            document_cache=self._document_cache,
        )
        return _WriterImplementation(config, document_cache=self._document_cache)
