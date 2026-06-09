from __future__ import annotations

import dataclasses
import functools
import pathlib
import typing as t

Characteristic: t.TypeAlias = t.Literal[
    "pyproject", "python-package", "tox", "readthedocs", "vcs-root"
]
_VCS_INDICATORS: tuple[str, ...] = (".git", ".hg", ".svn")


class DirExplorer:
    def __init__(self, default_start_dir: pathlib.Path) -> None:
        self.default_start_dir = default_start_dir

        # all nodes in a flat cache
        self._node_cache: dict[pathlib.Path, DiscoveryNode] = {}

    @functools.cached_property
    def pyproject_path(self) -> pathlib.Path | None:
        try:
            return self.search_for("pyproject").dirpath / "pyproject.toml"
        except LookupError:
            return None

    def search_for(
        self, characteristic: Characteristic, *, start_dir: pathlib.Path | None = None
    ) -> DiscoveryNode:
        if start_dir is None:
            start_dir = self.default_start_dir

        for node in DiscoveryNode._vcs_bounded_ancestors(
            start_dir, node_cache=self._node_cache
        ):
            node.run_dir_content_detection()
            if characteristic in node.characteristics:
                return node

        raise LookupError(
            f"mddj searched for a directory which matched the '{characteristic}' rule "
            "and could not find one."
        )


class _DirContentsDetector(t.Protocol):
    characteristics: tuple[Characteristic, ...]

    def match(self, dir_contents: frozenset[str]) -> bool: ...  # noqa: E704


@dataclasses.dataclass
class _SimplePathDetector:
    names: tuple[str, ...]
    characteristics: tuple[Characteristic, ...]

    def match(self, dir_contents: frozenset[str]) -> bool:
        return any(name in dir_contents for name in self.names)


class _SetupPyPackageDetector:
    characteristics: tuple[Characteristic, ...] = ("python-package",)

    def match(self, dir_contents: frozenset[str]) -> bool:
        # setup.py *without* __init__.py
        # or
        # setup.py in the repo root
        if "setup.py" not in dir_contents:
            return False
        return "__init__.py" not in dir_contents or bool(
            dir_contents.intersection(_VCS_INDICATORS)
        )


_DIR_CONTENTS_DETECTORS: tuple[_DirContentsDetector, ...] = (
    _SimplePathDetector(_VCS_INDICATORS, ("vcs-root",)),
    _SimplePathDetector(("pyproject.toml",), ("pyproject", "python-package")),
    _SimplePathDetector(("setup.cfg",), ("python-package",)),
    _SetupPyPackageDetector(),
    _SimplePathDetector((".readthedocs.yaml", ".readthedocs.yml"), ("readthedocs",)),
    _SimplePathDetector(("tox.ini", "tox.toml"), ("tox",)),
)

_NAMES_OF_INTEREST: set[str] = {
    name
    for detector in _DIR_CONTENTS_DETECTORS
    if isinstance(detector, _SimplePathDetector)
    for name in detector.names
} | {"setup.py"}


@dataclasses.dataclass
class DiscoveryNode:
    dirpath: pathlib.Path
    _characteristics: list[Characteristic] = dataclasses.field(default_factory=list)

    @property
    def characteristics(self) -> tuple[Characteristic, ...]:
        return tuple(self._characteristics)

    def run_dir_content_detection(self) -> None:
        # whenever dir contents are first fetched, detection runs
        # imperatively asking for this evaluation simply "touches" the property
        self._dir_contents

    @functools.cached_property
    def _dir_contents(self) -> frozenset[str]:
        """get dir contents and add to inferred characteristics"""
        dir_contents = frozenset(p.name for p in self.dirpath.iterdir())
        # if there's nothing of interest in a dir, bail quickly (expect this to
        # be the majority case, make it fast)
        if not _NAMES_OF_INTEREST & dir_contents:
            return dir_contents

        for detector in _DIR_CONTENTS_DETECTORS:
            if not detector.match(dir_contents):
                continue
            for result in detector.characteristics:
                if result not in self._characteristics:
                    self._characteristics.append(result)

        return dir_contents

    @classmethod
    def _vcs_bounded_ancestors(
        cls, start_dir: pathlib.Path, *, node_cache: dict[pathlib.Path, DiscoveryNode]
    ) -> t.Iterator[DiscoveryNode]:
        for d in _ancestors(start_dir):
            if d in node_cache:
                item = node_cache[d]
            else:
                item = cls(dirpath=d)
                node_cache[d] = item

            yield item

            # after the yield, run inference if it hasn't run before
            # if the node looks like a VCS root, stop crawling
            item.run_dir_content_detection()
            if "vcs-root" in item.characteristics:
                break


def _ancestors(start_dir: pathlib.Path) -> t.Iterator[pathlib.Path]:
    yield start_dir
    yield from start_dir.parents
