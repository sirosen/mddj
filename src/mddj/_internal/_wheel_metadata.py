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
    for extra_name in provides_extra:
        extras_map[extra_name] = tuple(
            _read_extra_from_dists(extra_name, requires_dist)
        )

    extra_deps = [dep for extra_deps in extras_map.values() for dep in extra_deps]
    non_extra_deps = tuple(dep for dep in requires_dist if dep not in extra_deps)

    for k, v in extras_map.items():
        extras_map[k] = tuple(_strip_extra_from_markers(dist, k) for dist in v)

    return WheelDependencyData(types.MappingProxyType(extras_map), non_extra_deps)


def _read_extra_from_dists(
    extra_name: str, requires_dist: t.Iterable[str]
) -> t.Iterator[str]:
    marker_patterns = tuple(
        re.compile(pat)
        for quote in ('"', "'")
        for pat in (
            rf"^\s*extra\s*==\s*{quote}{extra_name}{quote}\s*$",
            rf"^\s*extra\s*==\s*{quote}{extra_name}{quote}\s+and\s",
            rf"\sand\s+extra\s*==\s*{quote}{extra_name}{quote}\s*$",
        )
    )
    for dist_string in requires_dist:
        # substring matching to reject most things quickly
        if "extra" not in dist_string or extra_name not in dist_string:
            continue
        markers = str(Requirement(dist_string).marker)
        for pat in marker_patterns:
            if pat.search(markers):
                yield dist_string
                break


def _strip_extra_from_markers(dist_string: str, extra_name: str) -> str:
    """Attempt to remove an `extra == '...'` from a dist string's markers."""
    req = Requirement(dist_string)
    exact_patterns = tuple(
        re.compile(rf"^\s*extra\s*==\s*{quote}{extra_name}{quote}\s*$")
        for quote in ('"', "'")
    )
    if any(pat.search(str(req.marker).strip()) for pat in exact_patterns):
        req.marker = None
        return str(req)

    ending_patterns = tuple(
        re.compile(rf"^\s*(.*)\s*and\s+extra\s*==\s*{quote}{extra_name}{quote}\s*$")
        for quote in ('"', "'")
    )
    starting_patterns = tuple(
        re.compile(rf"^\s*extra\s*==\s*{quote}{extra_name}{quote}\s+and\s+(.*)\s*$")
        for quote in ('"', "'")
    )
    marker_str = str(req.marker)
    new_marker: str | None = None
    for pat in ending_patterns:
        if re_match := pat.search(marker_str):
            new_marker = re_match.group(1)
            break
    else:
        for pat in starting_patterns:
            if re_match := pat.search(marker_str):
                new_marker = re_match.group(1)
                break

    if new_marker is None:
        return dist_string

    if new_marker.startswith("(") and new_marker.endswith(")"):
        new_marker = new_marker[1:-1]
    req.marker = Marker(new_marker)
    return str(req)
