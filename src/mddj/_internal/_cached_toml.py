from __future__ import annotations

import pathlib

import tomlkit


class TomlDocumentCache:
    def __init__(self) -> None:
        self._cache: dict[pathlib.Path, tomlkit.TOMLDocument] = {}

    def load(self, path: pathlib.Path) -> tomlkit.TOMLDocument:
        if not path.is_absolute():
            raise ValueError("Cached loads must use absolute paths for consistency.")

        if path not in self._cache:
            with path.open("r", encoding="utf-8") as fp:
                data = tomlkit.load(fp)
            self._cache[path] = data
        return self._cache[path]
