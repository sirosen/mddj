from __future__ import annotations

import functools
import re
import types
import typing as t

from ..._internal import _cached_methods, _cached_toml
from ..config import ReaderConfig, ReadthedocsConfig
from .dynamic_package_reader import DynamicPackageReader
from .readthedocs_reader import ReadthedocsReader
from .static_pyproject_reader import StaticPyprojectReader
from .system_info_reader import SystemInfoReader
from .tox_reader import ToxReader


class MissingRequiredField(LookupError):
    pass


class NotALowerBound(ValueError):
    pass


class Reader:
    """
    A Reader is an interface for data reading capabilities.

    By default, the reader will prefer to use static metadata and will failover to
    dynamic data (which requires a build). Use ``static`` or ``dynamic`` to explicitly
    choose one or the other.

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
        self._document_cache = document_cache or _cached_toml.TomlDocumentCache()
        self.config = config
        self._method_cache: dict[t.Any, t.Any] = {}

    @functools.cached_property
    def tox(self) -> ToxReader:
        """a :class:`ToxReader` provided by this reader"""
        return ToxReader()

    @functools.cached_property
    def sys(self) -> SystemInfoReader:
        return SystemInfoReader()

    @functools.cached_property
    def readthedocs(self) -> ReadthedocsReader:
        return ReadthedocsReader(
            ReadthedocsConfig.load_from_toml(
                dir_explorer=self.config.dir_explorer,
                document_cache=self._document_cache,
            )
        )

    @functools.cached_property
    def static(self) -> StaticPyprojectReader:
        """a :class:`StaticPyprojectReader` provided by this reader"""
        return StaticPyprojectReader(
            self.config.dir_explorer, document_cache=self._document_cache
        )

    @functools.cached_property
    def dynamic(self) -> DynamicPackageReader:
        """a :class:`DynamicPackageReader` provided by this reader"""
        return DynamicPackageReader(
            self.config.dir_explorer,
            isolated_builds=self.config.isolated_builds,
            capture_build_output=self.config.capture_build_output,
        )

    # supported metadata APIs, in alphabetical order

    @_cached_methods.cached_method
    def authors(self) -> tuple[types.MappingProxyType[str, str], ...]:
        value = self.static.authors()
        if value is None:
            value = self.dynamic.authors()
        return value

    @_cached_methods.cached_method
    def classifiers(self, *, python_versions: bool = False) -> tuple[str, ...]:
        """
        Get the classifiers for the project.

        :param python_versions: Set ``python_versions=True`` to extract MAJOR.MINOR
            Python versions from classifiers.

        Note that ``python_versions`` skips major-version-only classifiers.
        """
        value = self.static.classifiers()
        if value is None:
            value = self.dynamic.classifiers()

        if python_versions:
            return _extract_python_versions_from_classifiers(value)
        return value

    @_cached_methods.cached_method
    def dependencies(self) -> tuple[str, ...]:
        """
        Get the dependencies for the project.

        Because extras use some of the same metadata fields, when dynamic metadata is
        used this listing is filtered to remove the values which are associated with
        optional-dependencies.
        """
        value = self.static.dependencies()
        if value is None:
            value = self.dynamic.dependencies()
        return value

    @_cached_methods.cached_method
    def description(self) -> str | None:
        value = self.static.description()
        if value is None:
            value = self.dynamic.description()
        return value

    @_cached_methods.cached_method
    def import_names(self) -> tuple[str, ...]:
        value = self.static.import_names()
        if value is None:
            value = self.dynamic.import_names()
        return value

    @_cached_methods.cached_method
    def import_namespaces(self) -> tuple[str, ...]:
        value = self.static.import_namespaces()
        if value is None:
            value = self.dynamic.import_namespaces()
        return value

    @_cached_methods.cached_method
    def keywords(self) -> tuple[str, ...]:
        value = self.static.keywords()
        if value is None:
            value = self.dynamic.keywords()
        return value

    @_cached_methods.cached_method
    def maintainers(self) -> tuple[types.MappingProxyType[str, str], ...]:
        value = self.static.maintainers()
        if value is None:
            value = self.dynamic.maintainers()
        return value

    @_cached_methods.cached_method
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
        if (static := self.static.optional_dependencies()) is not None:
            return static

        return self.dynamic.optional_dependencies(
            exact_wheel_metadata=exact_wheel_metadata
        )

    @_cached_methods.cached_method
    def name(self) -> str:
        value = self.static.name()
        if value is None:
            value = self.dynamic.name()
        if value is None:
            raise MissingRequiredField(
                "No 'name' found in static or dynamic metadata. "
                "The project is not a Python Package or did not build correctly."
            )
        return value

    @_cached_methods.cached_method
    def requires_python(self, *, lower_bound: bool = False) -> str | None:
        """
        Get the Requires-Python bound for the project.

        :param lower_bound: When true, only get the lower bound of a `>=` expression.
            Only `>=` is supported. Any other comparator will produce a ValueError if
            `lower_bound` is set.
        """
        value = self._requires_python
        if lower_bound and value is not None:
            return _requires_python_lower_bound(value)
        return value

    @functools.cached_property
    def _requires_python(self) -> str | None:
        value = self.static.requires_python()
        if value is None:
            value = self.dynamic.requires_python()
        return value

    @_cached_methods.cached_method
    def version(self) -> str:
        """Get the version of the project."""
        value = self.static.version()
        if value is None:
            value = self.dynamic.version()
        if value is None:
            raise MissingRequiredField(
                "No 'version' found in static or dynamic metadata. "
                "The project is not a Python Package or did not build correctly."
            )
        return value


def _requires_python_lower_bound(req: str) -> str:
    reqs = req.split(",")
    lower_bounds = []
    for r in reqs:
        if r.startswith(">="):
            lower_bounds.append(r[2:])
        elif r.startswith(">"):
            raise NotALowerBound(
                "Found a > requirement, rejecting as invalid (use '>=' instead)"
            )
    if len(lower_bounds) > 1:
        raise NotALowerBound("Found multiple lower bounds, cannot choose one")
    elif len(lower_bounds) == 0:
        raise NotALowerBound("Found no lower bounds")
    else:
        return lower_bounds[0]


_CLASSIFIER_PATTERN = re.compile(r"Programming Language :: Python :: (\d+\.\d+)")


def _extract_python_versions_from_classifiers(
    classifiers: tuple[str, ...],
) -> tuple[str, ...]:
    result = []
    for value in classifiers:
        if not (match := _CLASSIFIER_PATTERN.fullmatch(value)):
            continue
        result.append(match.group(1))
    return tuple(result)
