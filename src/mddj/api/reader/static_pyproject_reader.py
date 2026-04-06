from __future__ import annotations

import collections.abc
import functools
import pathlib
import types
import typing as t

import tomlkit
from packaging.utils import canonicalize_name

from ..._internal import _cached_methods, _cached_toml, _types


class StaticMetadataMalformed(ValueError):
    pass


class StaticPyprojectReader:
    def __init__(
        self,
        pyproject_path: pathlib.Path,
        document_cache: _cached_toml.TomlDocumentCache | None = None,
    ) -> None:
        self._pyproject_path = pyproject_path
        self._document_cache = document_cache or _cached_toml.TomlDocumentCache()

        self._method_cache: dict[t.Any, t.Any] = {}

    # supported public APIs follow, in alphabetical order

    @_cached_methods.cached_method
    def authors(self, /) -> tuple[types.MappingProxyType[str, str], ...] | None:
        return self._read_contact_info("authors")

    @_cached_methods.cached_method
    def classifiers(self) -> tuple[str, ...] | None:
        return self._read_string_array("classifiers")

    @_cached_methods.cached_method
    def dependencies(self) -> tuple[str, ...] | None:
        return self._read_string_array("dependencies")

    @_cached_methods.cached_method
    def description(self) -> str | None:
        return self._read_string("description")

    @_cached_methods.cached_method
    def dynamic(self) -> tuple[str, ...] | None:
        return self._read_string_array("dynamic")

    @_cached_methods.cached_method
    def import_names(self) -> tuple[str, ...] | None:
        return self._read_string_array("import-names")

    @_cached_methods.cached_method
    def import_namespaces(self) -> tuple[str, ...] | None:
        return self._read_string_array("import-namespaces")

    @_cached_methods.cached_method
    def keywords(self) -> tuple[str, ...] | None:
        return self._read_string_array("keywords")

    @_cached_methods.cached_method
    def optional_dependencies(
        self,
    ) -> types.MappingProxyType[str, tuple[str, ...]] | None:
        return self._optional_dependencies

    @_cached_methods.cached_method
    def name(self) -> str | None:
        return self._read_string("name")

    @_cached_methods.cached_method
    def requires_python(self) -> str | None:
        return self._read_string("requires-python")

    @_cached_methods.cached_method
    def version(self) -> str | None:
        return self._read_string("version")

    # internal lookup APIs

    @functools.cached_property
    def _document(self) -> tomlkit.TOMLDocument:
        return self._document_cache.load(self._pyproject_path)

    def _read(self, key: str) -> object | None:
        try:
            value = _read_pyproject_toml_value(self._document, "project", key)
        except (FileNotFoundError, LookupError):
            value = None

        return value

    def _read_string(self, key: str) -> str | None:
        value = self._read(key)

        if value is None:
            pass
        elif isinstance(value, str):
            value = str(value)  # convert away from string subtypes
        else:
            raise StaticMetadataMalformed(
                f"Could not read {key!r}, data was not a string!"
            )

        return value

    def _read_string_array(self, key: str) -> tuple[str, ...] | None:
        value = self._read(key)

        if value is None:
            pass
        elif _types.is_toml_array(value) and all(isinstance(x, str) for x in value):
            value = tuple(str(x) for x in value)
        else:
            raise StaticMetadataMalformed(
                f"Could not read {key!r}, data was not an array of strings!"
            )

        return value

    def _read_contact_info(
        self, key: str
    ) -> tuple[types.MappingProxyType[str, str], ...] | None:
        value = self._read(key)
        if value is not None:
            if not _types.is_toml_array(value):
                raise StaticMetadataMalformed(
                    f"Got non-array value for '{key}' in pyproject.toml."
                )
            elif not all(_is_well_formed_contact_info_entry(x) for x in value):
                raise StaticMetadataMalformed(
                    f"Got a malformed value in '{key}' in pyproject.toml."
                )

            value = tuple(types.MappingProxyType(x) for x in value)
        return value

    @functools.cached_property
    def _optional_dependencies(
        self,
    ) -> types.MappingProxyType[str, tuple[str, ...]] | None:
        value = self._read("optional-dependencies")
        if value is None:
            return None

        if not _types.is_toml_mapping(value):
            raise StaticMetadataMalformed(
                "Cannot read project.optional-dependencies because it is not a TOML "
                "table."
            )
        map: dict[str, tuple[str, ...]] = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise StaticMetadataMalformed(
                    f"Got non-string key in project.optional-dependencies: {k!r}"
                )
            if not _types.is_toml_array(v):
                raise StaticMetadataMalformed(
                    f"Value for project.optional-dependencies[{k}] is not an array."
                )
            if any(not isinstance(x, str) for x in v):
                raise StaticMetadataMalformed(
                    f"Got a non-string value in project.optional-dependencies[{k}]."
                )
            map[k] = tuple(v)

        # static data is not already normalized, so it must be done by mddj or it
        # won't be any good for lookups/comparisons
        canonicalized_map: dict[str, tuple[str, ...]] = {}
        for name, value in map.items():
            canonical = canonicalize_name(name)
            if canonical in canonicalized_map:
                raise StaticMetadataMalformed(
                    f"optional-dependencies for '{canonical}' appear "
                    "multiple times in TOML data. This is valid TOML but not valid "
                    "package metadata. "
                    "Read more: https://packaging.python.org/en/latest/specifications/core-metadata/#provides-extra-multiple-use"  # noqa: E501
                )
            canonicalized_map[canonical] = value
        return types.MappingProxyType(canonicalized_map)


def _is_well_formed_contact_info_entry(entry: object) -> bool:
    if not isinstance(entry, dict):
        return False
    if not (entry.keys() <= {"name", "email"}):
        return False
    if not all(isinstance(value, str) for value in entry.values()):
        return False
    return True


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
