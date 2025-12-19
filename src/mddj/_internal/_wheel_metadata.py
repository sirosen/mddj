from __future__ import annotations

import dataclasses
import pathlib
import re
import types
import typing as t

from packaging.markers import Marker
from packaging.requirements import Requirement

try:
    import importlib_metadata as _importlib_metadata
except ImportError:
    import importlib.metadata as _importlib_metadata


@dataclasses.dataclass
class WheelDependencyData:
    # the parsed extras, as indicated by
    #   Provides-Extra
    #   Requires-Dist
    extras: types.MappingProxyType[str, tuple[str, ...]]
    # a variant of the parsed extras, as above, but with the `extra == ...` markers
    # removed where possible
    cleaned_extras: types.MappingProxyType[str, tuple[str, ...]]
    # the non-extra dependencies, as indicated by
    #   Requires-Dist
    # after filtering Provides-Extra
    dependencies: tuple[str, ...]


def get_package_metadata(
    source_dir: pathlib.Path, isolated: bool = True, quiet: bool = True
) -> _importlib_metadata.PackageMetadata:
    """
    Get metadata for wheel, either using the PEP 517 hook or by actually
    doing a wheel build and examining the result.
    """
    import build.util
    import pyproject_hooks

    runner = pyproject_hooks.quiet_subprocess_runner
    if not quiet:
        runner = pyproject_hooks.default_subprocess_runner
    return build.util.project_wheel_metadata(
        source_dir, isolated=isolated, runner=runner
    )


def load_wheel_dependency_data(
    metadata: _importlib_metadata.PackageMetadata,
) -> WheelDependencyData:
    provides_extra = metadata.get_all("Provides-Extra", [])
    requires_dist = metadata.get_all("Requires-Dist", [])

    extras_map: dict[str, tuple[str, ...]] = {}
    cleaned_extras_map: dict[str, tuple[str, ...]] = {}
    for extra_name in provides_extra:
        original_dists: list[str] = []
        cleaned_dists: list[str] = []
        for original, cleaned in _read_extra_from_dists(extra_name, requires_dist):
            original_dists.append(original)
            cleaned_dists.append(cleaned)
        extras_map[extra_name] = tuple(original_dists)
        cleaned_extras_map[extra_name] = tuple(cleaned_dists)

    extra_deps = [dep for extra_deps in extras_map.values() for dep in extra_deps]
    non_extra_deps = tuple(dep for dep in requires_dist if dep not in extra_deps)

    return WheelDependencyData(
        types.MappingProxyType(extras_map),
        types.MappingProxyType(cleaned_extras_map),
        non_extra_deps,
    )


def _read_extra_from_dists(
    extra_name: str, requires_dist: t.Iterable[str]
) -> t.Iterator[tuple[str, str]]:
    """
    Given an extra name, find all of the matching dependency dist strings.

    Return them as pairs of (original_value, interpreted_value) where
    the interpreted value is an attempt to strip off the extra name.
    """
    subpattern = _extra_pattern(extra_name)
    exact_pattern = re.compile(rf"^\s*{subpattern}\s*$")
    trailing_pattern = re.compile(rf"^\s*(.*)\s+and\s+{subpattern}\s*$")
    leading_pattern = re.compile(rf"^\s*{subpattern}\s+and\s+(.*)\s*$")

    for dist_string in requires_dist:
        # substring matching to reject most things very quickly, without regex matching
        if "extra" not in dist_string or extra_name not in dist_string:
            continue
        req = Requirement(dist_string)
        marker_string = str(req.marker)

        # if an exact match works, strip markers entirely
        if exact_pattern.search(marker_string):
            print(f"{exact_pattern=} matched {marker_string=}")
            req.marker = None
            yield (dist_string, str(req))
            continue

        # if the leading or trailing pattern matches, the modified marker is the
        # matched group, with parens stripped if possible
        if (re_match := leading_pattern.search(marker_string)) or (
            re_match := trailing_pattern.search(marker_string)
        ):
            new_marker = re_match.group(1)
            if new_marker is None:
                print(f"{marker_string=} {leading_pattern=} {trailing_pattern=}")
            # remove parens, and potentially extraneous whitespace within
            if new_marker.startswith("(") and new_marker.endswith(")"):
                new_marker = new_marker[1:-1].strip()
            req.marker = Marker(new_marker)
            yield (dist_string, str(req))


def _extra_pattern(extra_name: str) -> str:
    escaped_extra_name = re.escape(extra_name)
    quoted_extra_name = f"(?:(?:'{escaped_extra_name}')|(?:\"{escaped_extra_name}\"))"
    return r"extra\s*==\s*" + quoted_extra_name
