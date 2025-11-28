from __future__ import annotations

import collections.abc
import pathlib
import re
import shutil
import subprocess
import typing as t

import build.util
import pyproject_hooks
import tomlkit

from ._compat import metadata
from ._types import TomlValue, is_toml_array, is_toml_mapping


class ToxReaderError(RuntimeError):
    pass


def get_wheel_metadata(
    source_dir: pathlib.Path, isolated: bool = True, quiet: bool = True
) -> metadata.PackageMetadata:
    """
    Get metadata for wheel, either using the PEP 517 hook or by actually
    doing a wheel build and examining the result.
    """
    runner = pyproject_hooks.quiet_subprocess_runner
    if not quiet:
        runner = pyproject_hooks.default_subprocess_runner
    return build.util.project_wheel_metadata(
        source_dir, isolated=isolated, runner=runner
    )


def get_tox_tested_versions() -> list[str]:
    """
    Use `tox --listenvs` to get a list of all tox environments.
    Then use that listing to get a list of python versions.
    """
    tox = shutil.which("tox")
    if not tox:
        raise ToxReaderError("Cannot fetch tox data. A 'tox' command was not found.")
    _check_tox_version(tox)

    output = subprocess.check_output([tox, "--listenvs"], text=True)

    versions = set()
    for line in output.splitlines():
        for part in line.split("-"):
            if match := re.match(r"py(\d)\.?(\d+)", part):
                versions.add(match.group(1) + "." + match.group(2))
    return list(versions)


def _check_tox_version(tox_command: str) -> t.Literal[3, 4]:
    """
    Check that the 'tox' command is a supported version.
    Any unexpected outputs will raise an error, which allows for a cleaner early abort.
    """
    tox_version_proc = subprocess.run(
        [tox_command, "--version"], text=True, capture_output=True
    )
    if tox_version_proc.returncode != 0:
        raise ToxReaderError("Cannot fetch tox data. 'tox --version' failed.")

    full_tox_version = tox_version_proc.stdout.strip()
    if full_tox_version.startswith("3."):
        return 3
    elif full_tox_version.startswith("4."):
        return 4
    else:
        raise ToxReaderError("'tox --version' was not a recognized version.")


def read_pyproject_toml_value(pyproject_path: pathlib.Path, *path: str | int) -> object:
    """
    Read an arbitrary value from 'pyproject.toml'
    """
    with pyproject_path.open("rb") as fp:
        data = tomlkit.load(fp)

    # traverse the TOML data structure
    cursor: TomlValue = data
    for subkey in path:
        # pedantically enumerate the branches for static type checking to
        # easily see the association between key and container types
        if isinstance(subkey, str) and is_toml_mapping(cursor):  # slyp: disable=W200
            cursor = cursor[subkey]
        elif isinstance(subkey, int) and is_toml_array(cursor):
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
