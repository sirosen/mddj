from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import typing as t

import build.util

from mddj._compat import metadata


class ToxReaderError(RuntimeError):
    pass


def get_wheel_metadata(
    source_dir: pathlib.Path, isolated: bool = True, quiet: bool = True
) -> metadata.PackageMetadata:
    """
    'quiet' is currently a no-op.

    After the next release of build, change usage to this:

        import pyproject_hooks

        ...

        runner = pyproject_hooks.quiet_subprocess_runner
        if not quiet:
            runner = pyproject_hooks.default_subprocess_runner
        return build.util.project_wheel_metadata(
            source_dir, isolated=isolated, runner=runner
        ).json
    """
    return build.util.project_wheel_metadata(source_dir, isolated=isolated)


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

    versions = []
    for line in output.splitlines():
        for part in line.split("-"):
            if match := re.match(r"py(\d)(\d+)", part):
                versions.append(match.group(1) + "." + match.group(2))
    return versions


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
