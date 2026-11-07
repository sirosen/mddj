from __future__ import annotations

import collections.abc
import functools
import sys
import types
import typing as t

import tomlkit
from packaging.utils import canonicalize_name

from ..._internal import _cached_methods, _cached_toml, _discovery, _types
from .._errors import MDDJError

if sys.version_info >= (3, 13):
    from typing import TypeIs
else:
    from typing_extensions import TypeIs


class StaticMetadataMalformed(MDDJError, ValueError):
    pass


class StaticPyprojectReader(t.Protocol):
    _dir_explorer: _discovery.DirExplorer
    _document_cache: _cached_toml.TomlDocumentCache

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
    def entry_points(
        self,
        *,
        include: tuple[t.Literal["gui_scripts", "console_scripts"], ...] = (
            "gui_scripts",
            "console_scripts",
        ),
    ) -> types.MappingProxyType[str, types.MappingProxyType[str, str]] | None:
        """
        Fetch the [project.entry-points] table, with an include option which can select
        the ``[project.gui_scripts]`` and ``[project.scripts]`` tables for inclusion as
        well. By default, these tables are included.

        Note that ``console_scripts`` in ``include`` corresponds with the
        ``[project.scripts]`` table.

        :param include: A tuple of table names, other than ``[project.entry-points]``,
            which are part of the entry-points specification and should be included in
            the result. To get only ``[project.entry-points]``, pass ``include=()``.
        """
        include_values_: dict[str, types.MappingProxyType[str, str] | None] = {}
        if "gui_scripts" in include:
            include_values_["gui_scripts"] = self.gui_scripts()
        if "console_scripts" in include:
            include_values_["console_scripts"] = self.scripts()
        include_values = {k: v for k, v in include_values_.items() if v is not None}

        value = self._read("entry-points")
        if value is None:
            if include_values:
                return types.MappingProxyType(include_values)
            return None

        if not _types.is_toml_mapping(value):
            raise StaticMetadataMalformed(
                "Cannot read project.entry-points because it is not a TOML table."
            )
        for k, v in value.items():
            if not _is_str_to_str_mapping(v):
                raise StaticMetadataMalformed(
                    f"Cannot read project.entry-points.{k!r} because it is not a TOML "
                    "table with string values."
                )
        if "gui_scripts" in value:
            raise StaticMetadataMalformed(
                "Cannot read project.entry-points. "
                "'gui_scripts' was present, making data ambiguous under spec."
            )
        if "console_scripts" in value:
            raise StaticMetadataMalformed(
                "Cannot read project.entry-points. "
                "'console_scripts' was present, making data ambiguous under spec."
            )
        value.update(include_values)
        return types.MappingProxyType(value)

    @_cached_methods.cached_method
    def gui_scripts(
        self,
    ) -> types.MappingProxyType[str, str] | None:
        value = self._read("gui-scripts")
        if value is None:
            return None
        if not _is_str_to_str_mapping(value):
            raise StaticMetadataMalformed(
                "Cannot read project.gui-scripts because it is not a TOML table with "
                "string values."
            )
        return types.MappingProxyType(value)

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
    def maintainers(self, /) -> tuple[types.MappingProxyType[str, str], ...] | None:
        return self._read_contact_info("maintainers")

    @_cached_methods.cached_method
    def optional_dependencies(
        self,
    ) -> types.MappingProxyType[str, tuple[str, ...]] | None:
        return self._optional_dependencies

    @_cached_methods.cached_method
    def name(self) -> str | None:
        return self._read_string("name")

    @_cached_methods.cached_method
    def readme(
        self, *, content: bool = False
    ) -> str | types.MappingProxyType[str, str] | None:
        """
        Get the readme.

        When reading a separate readme file, raises an error if the file does not exist.
        Returns ``None`` if there is no readme declared.

        :param content: When true, get the content of the readme, rather than readme
            metadata as stored in ``pyproject.toml``.
        """
        value = self._read("readme")
        if value is None:
            return None
        elif isinstance(value, str):
            if content:
                return self._readme_file_content(value)
            else:
                return value
        elif _is_str_to_str_mapping(value):
            if content:
                if "file" in value and "text" in value:
                    raise StaticMetadataMalformed(
                        "project.readme is invalid. "
                        "'file' and 'text' are mutually exclusive."
                    )
                elif "file" in value:
                    return self._readme_file_content(value["file"])
                elif "text" in value:
                    return value["text"]
                else:
                    raise StaticMetadataMalformed(
                        "pyproject.readme is invalid. 'file' or 'text' must be present."
                    )
            else:
                return types.MappingProxyType(value)
        else:
            raise StaticMetadataMalformed(
                "Cannot read project.readme because it is not a TOML table with "
                "string values or a single string."
            )

    @_cached_methods.cached_method
    def _readme_file_content(self, relpath: str) -> str | None:
        pyproject_path = self._dir_explorer.pyproject_path
        if not pyproject_path:
            return None
        return (pyproject_path.parent / relpath).read_text()

    @_cached_methods.cached_method
    def requires_python(self) -> str | None:
        return self._read_string("requires-python")

    @_cached_methods.cached_method
    def scripts(
        self,
    ) -> types.MappingProxyType[str, str] | None:
        value = self._read("scripts")
        if value is None:
            return None
        if not _is_str_to_str_mapping(value):
            raise StaticMetadataMalformed(
                "Cannot read project.scripts because it is not a TOML table with "
                "string values."
            )
        return types.MappingProxyType(value)

    @_cached_methods.cached_method
    def version(self) -> str | None:
        return self._read_string("version")

    # internal lookup APIs

    @functools.cached_property
    def _document(self) -> tomlkit.TOMLDocument:
        if (path := self._dir_explorer.pyproject_path) is None:
            raise LookupError("no pyproject.toml found")
        return self._document_cache.load(path)

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


class _StaticPyprojectReaderImplementation(StaticPyprojectReader):
    def __init__(
        self,
        dir_explorer: _discovery.DirExplorer,
        document_cache: _cached_toml.TomlDocumentCache | None = None,
    ) -> None:
        self._dir_explorer = dir_explorer
        self._document_cache = document_cache or _cached_toml.TomlDocumentCache()


def _is_well_formed_contact_info_entry(entry: object) -> bool:
    if not isinstance(entry, dict):
        return False
    if not (entry.keys() <= {"name", "email"}):
        return False
    if not all(isinstance(value, str) for value in entry.values()):
        return False
    return True


def _is_str_to_str_mapping(value: object) -> TypeIs[t.Mapping[str, str]]:
    if not _types.is_toml_mapping(value):
        return False
    return all(isinstance(k, str) and isinstance(v, str) for k, v in value.items())


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
