from __future__ import annotations

import pathlib
import typing as t


def discover_project_dir(start_dir: pathlib.Path) -> pathlib.Path:
    for directory, dir_contents in _vcs_bounded_ancestors_with_contents(start_dir):
        # Rule 1: the first ancestor dir with a `pyproject.toml`
        if "pyproject.toml" in dir_contents:
            return directory

        # Rule 2: a `setup.cfg`
        if "setup.cfg" in dir_contents:
            return directory

        # Rule 3: `setup.py` in a directory without an `__init__.py`
        if "setup.py" in dir_contents and "__init__.py" not in dir_contents:
            return directory

        # Rule 4: a `tox.ini` file is present, meaning we can read tox data
        #         (maybe there is no python package but there is tox config)
        if "tox.ini" in dir_contents:
            return directory

    # Rule 5: the root has a `setup.py`; that will be our final guess
    if "setup.py" in dir_contents:
        return directory

    raise LookupError(
        "mddj could not find the project root. "
        "Ensure you are running from a subdirectory of a Python package source dir."
    )


def _vcs_bounded_ancestors_with_contents(
    start_dir: pathlib.Path,
) -> t.Iterator[tuple[pathlib.Path, set[str]]]:
    for d in _ancestors(start_dir):
        dir_contents = {p.name for p in d.iterdir()}
        if dir_contents.intersection((".git", ".hg", ".svn")):
            yield d, dir_contents
            return
        yield d, dir_contents


def _ancestors(start_dir: pathlib.Path) -> t.Iterator[pathlib.Path]:
    yield start_dir
    yield from start_dir.parents
