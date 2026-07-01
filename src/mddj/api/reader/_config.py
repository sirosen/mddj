from __future__ import annotations

import dataclasses

from ..._internal import _cached_toml, _discovery


@dataclasses.dataclass
class ReaderConfig:
    """
    Configuration for a metadata reader.
    """

    dir_explorer: _discovery.DirExplorer
    document_cache: _cached_toml.TomlDocumentCache
    isolated_builds: bool
    capture_build_output: bool
