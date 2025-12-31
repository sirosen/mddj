from __future__ import annotations

import collections.abc
import functools
import types
import typing as t

import tomlkit
from packaging.utils import canonicalize_name

from .._internal import _cached_toml, _types, _wheel_metadata
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
        self._lookup_cache: dict[str, t.Any] = {}

        self.tox = ToxReader()

    @functools.cached_property
    def _wheel_package_metadata(self) -> _importlib_metadata.PackageMetadata:
        return _wheel_metadata.get_package_metadata(
            self.config.project_directory,
            isolated=self.config.isolated_builds,
            quiet=self.config.capture_build_output,
        )

    @functools.cached_property
    def _parsed_wheel_dependency_data(self) -> _wheel_metadata.WheelDependencyData:
        return _wheel_metadata.load_wheel_dependency_data(self._wheel_package_metadata)

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
        if project_fieldname in self._lookup_cache:
            return self._lookup_cache[project_fieldname]  # type: ignore[no-any-return]

        value = self._read_static(project_fieldname)
        if value is not None:
            self._lookup_cache[project_fieldname] = value
        else:
            value = self._wheel_package_metadata.get(metadata_fieldname)
            self._lookup_cache[project_fieldname] = value
        return value

    def _lookup_string_array(
        self,
        project_fieldname: str,
        metadata_fieldname: str,
        mode: t.Literal["commasep", "multiuse"] = "multiuse",
    ) -> tuple[str, ...]:
        if project_fieldname in self._lookup_cache:
            return self._lookup_cache[project_fieldname]  # type: ignore[no-any-return]

        value: object | None = self._read_static(project_fieldname)
        if _types.is_toml_array(value):
            value = tuple(str(x) for x in value)
            self._lookup_cache[project_fieldname] = value
        else:
            match mode:
                case "multiuse":
                    value = tuple(
                        str(x)
                        for x in self._wheel_package_metadata.get_all(
                            metadata_fieldname, ()
                        )
                    )
                case "commasep":
                    value = self._wheel_package_metadata.get(metadata_fieldname)
                    if isinstance(value, str):
                        value = tuple(value.split(","))
                    else:
                        value = ()
                case _ as unreachable:
                    raise t.assert_never(unreachable)
            self._lookup_cache[project_fieldname] = value

        return value

    def classifiers(self) -> tuple[str, ...]:
        return self._lookup_string_array("classifiers", "Classifier")

    def dependencies(self) -> tuple[str, ...]:
        """Get the dependencies for the project."""
        value = self._read_static("dependencies")
        if _types.is_toml_array(value):
            return tuple(value)

        return self._parsed_wheel_dependency_data.dependencies

    def description(self) -> str:
        return str(self._lookup("description", "Summary"))

    def import_names(self) -> tuple[str, ...]:
        return self._lookup_string_array("import-names", "Import-Name")

    def import_namespaces(self) -> tuple[str, ...]:
        return self._lookup_string_array("import-namespaces", "Import-Namespace")

    def keywords(self) -> tuple[str, ...]:
        return self._lookup_string_array("keywords", "Keywords", mode="commasep")

    def optional_dependencies(
        self, *, exact_wheel_metadata: bool = False
    ) -> types.MappingProxyType[str, tuple[str, ...]]:
        """
        Retrieve the optional dependencies for the current project.

        When wheel dynamic metadata is used, and wheel metadata is therefore produced,
        the fields in metadata must be interpreted in order to find optional
        dependencies based on marker. ``mddj`` checks dependencies which start or end
        with an ``extra`` marker to find the optional dependencies.
        This heuristic is correct for typical cases but could be inaccurate with very
        unusual package builds.

        :param exact_wheel_metadata: Only applies to dynamic metadata builds. After
            finding optional dependencies, ``mddj`` will attempt to remove the markers
            which associate a dependency with an extra. Set this flag to ``True`` to
            retrieve the original data without this modification.
        """
        if (static := self._static_optional_dependencies) is not None:
            return static

        if exact_wheel_metadata:
            return self._parsed_wheel_dependency_data.extras
        else:
            return self._parsed_wheel_dependency_data.cleaned_extras

    @functools.cached_property
    def _static_optional_dependencies(
        self,
    ) -> types.MappingProxyType[str, tuple[str, ...]] | None:
        value = self._read_static("optional-dependencies")
        if _types.is_toml_mapping(value):
            map: dict[str, tuple[str, ...]] = {}
            for k, v in value.items():
                if not isinstance(k, str):
                    raise ValueError(
                        f"Got non-string key in project.optional-dependencies: {k!r}"
                    )
                if not _types.is_toml_array(v):
                    raise ValueError(
                        f"Value for project.optional-dependencies[{k}] is not an "
                        "array."
                    )
                if any(not isinstance(x, str) for x in v):
                    raise ValueError(
                        f"Got a non-string value in project.optional-dependencies[{k}]."
                    )
                map[k] = tuple(v)

            # static data is not already normalized, so it must be done by mddj or it
            # won't be any good for lookups/comparisons
            canonicalized_map: dict[str, tuple[str, ...]] = {}
            for name, value in map.items():
                canonical = canonicalize_name(name)
                if canonical in canonicalized_map:
                    raise ValueError(
                        f"optional-dependencies for '{canonical}' appear "
                        "multiple times in TOML data. This is valid TOML but not valid "
                        "package metadata. "
                        "Read more: https://packaging.python.org/en/latest/specifications/core-metadata/#provides-extra-multiple-use"  # noqa: E501
                    )
                canonicalized_map[canonical] = value
            return types.MappingProxyType(canonicalized_map)

        return None

    def name(self) -> str:
        return str(self._lookup("name", "Name"))

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
    def _requires_python(self) -> str:
        value = self._lookup("requires-python", "Requires-Python")
        if value is None:
            raise LookupError("No Requires-Python data found")
        return str(value)

    def version(self) -> str:
        """Get the version of the project."""
        return str(self._lookup("version", "Version"))


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
