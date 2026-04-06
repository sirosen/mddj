from __future__ import annotations

import email.utils
import functools
import pathlib
import types
import typing as t

from ..._internal import _cached_methods, _wheel_metadata

try:
    import importlib_metadata as _importlib_metadata
except ImportError:
    import importlib.metadata as _importlib_metadata


class DynamicPackageReader:
    def __init__(
        self,
        project_directory: pathlib.Path,
        *,
        isolated_builds: bool = True,
        capture_build_output: bool = True,
    ) -> None:
        self._project_directory = project_directory
        self._isolated_builds = isolated_builds
        self._capture_build_output = capture_build_output

        self._method_cache: dict[t.Any, t.Any] = {}

    # supported public APIs follow, in alphabetical order

    @_cached_methods.cached_method
    def authors(self) -> tuple[types.MappingProxyType[str, str], ...]:
        return self._read_contact_info("Author", "Author-email")

    @_cached_methods.cached_method
    def classifiers(self) -> tuple[str, ...]:
        return self._read_string_array("Classifier")

    @_cached_methods.cached_method
    def dependencies(self) -> tuple[str, ...]:
        return self._parsed_wheel_dependency_data.dependencies

    @_cached_methods.cached_method
    def description(self) -> str | None:
        return self._read("Summary")

    @_cached_methods.cached_method
    def dynamic(self) -> tuple[str, ...]:
        return self._read_string_array("Dynamic")

    @_cached_methods.cached_method
    def import_names(self) -> tuple[str, ...]:
        return self._read_string_array("Import-Name")

    @_cached_methods.cached_method
    def import_namespaces(self) -> tuple[str, ...]:
        return self._read_string_array("Import-Namespace")

    @_cached_methods.cached_method
    def keywords(self) -> tuple[str, ...]:
        return self._read_string_array("Keywords", mode="commasep")

    @_cached_methods.cached_method
    def optional_dependencies(
        self, *, exact_wheel_metadata: bool = False
    ) -> types.MappingProxyType[str, tuple[str, ...]]:
        """
        Retrieve the optional dependencies for the project.

        The fields in metadata must be interpreted in order to find optional
        dependencies based on markers. ``mddj`` checks dependencies which start or end
        with an ``extra`` marker to find the optional dependencies.
        This heuristic is correct for typical cases but could be inaccurate with very
        unusual package builds.

        :param exact_wheel_metadata: After finding optional dependencies, ``mddj``
            will attempt to remove the markers which associate a dependency with an
            extra. Set this flag to ``True`` to retrieve the original data without this
            modification.
        """
        if exact_wheel_metadata:
            return self._parsed_wheel_dependency_data.extras
        else:
            return self._parsed_wheel_dependency_data.cleaned_extras

    @_cached_methods.cached_method
    def name(self) -> str | None:
        return self._read("Name")

    @_cached_methods.cached_method
    def requires_python(self) -> str | None:
        return self._read("Requires-Python")

    @_cached_methods.cached_method
    def version(self) -> str | None:
        return self._read("Version")

    # internal lookup APIs

    @functools.cached_property
    def _wheel_package_metadata(self) -> _importlib_metadata.PackageMetadata:
        return _wheel_metadata.get_package_metadata(
            self._project_directory,
            isolated=self._isolated_builds,
            quiet=self._capture_build_output,
        )

    @functools.cached_property
    def _parsed_wheel_dependency_data(self) -> _wheel_metadata.WheelDependencyData:
        return _wheel_metadata.load_wheel_dependency_data(self._wheel_package_metadata)

    def _read(self, key: str) -> str | None:
        return self._wheel_package_metadata.get(key)  # type: ignore[no-any-return]

    def _read_string_array(
        self,
        key: str,
        mode: t.Literal["commasep", "multiuse"] = "multiuse",
    ) -> tuple[str, ...]:
        match mode:
            case "multiuse":
                value = tuple(
                    str(x) for x in self._wheel_package_metadata.get_all(key, ())
                )
            case "commasep":
                value = self._wheel_package_metadata.get(key)
                if isinstance(value, str):
                    value = tuple(value.split(","))
                else:
                    value = ()
            case _ as unreachable:
                t.assert_never(unreachable)

        return value

    def _read_contact_info(
        self,
        bare_fieldname: str,
        email_fieldname: str,
    ) -> tuple[types.MappingProxyType[str, str], ...]:
        emails = self._wheel_package_metadata.get(email_fieldname)
        names = self._wheel_package_metadata.get(bare_fieldname)

        email_mappings = _parse_emails_to_contact_info(emails) if emails else []
        names_in_emails = {
            mapping["name"] for mapping in email_mappings if "name" in mapping
        }

        # the name field is split on commas -- this may result in bad data if a person's
        # name contains a comma, but there is no safe way to handle this possibility
        if names is not None:
            for name in names.split(","):
                name = name.strip()
                if name not in names_in_emails:
                    email_mappings.append({"name": name})

        return tuple(types.MappingProxyType(x) for x in email_mappings)


def _parse_emails_to_contact_info(emails: str) -> list[dict[str, str]]:
    ret = []
    for name, address in email.utils.getaddresses([emails]):
        item: dict[str, str] = {}
        if name:
            item["name"] = name
        if address:
            item["email"] = address
        ret.append(item)
    return ret
