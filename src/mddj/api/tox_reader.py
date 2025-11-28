from __future__ import annotations

import functools
import re
import shutil
import subprocess
import sys
import typing as t


class ToxReaderError(RuntimeError):
    pass


class ToxReader:
    """
    A ToxReader is a specialized data reader for ``tox`` data.

    Typically, users should simply create a DJ and then access the tox reader built by
    it, as in:

    .. code-block:: pycon

        >>> from mddj.api import DJ
        >>> dj = DJ()
        >>> dj.read.tox.min_version()
        '3.8'
    """

    @functools.cached_property
    def _tox_cmd(self) -> tuple[str, ...]:
        try:
            import tox  # noqa: F401
        except ImportError:
            tox_cmd = shutil.which("tox")
            if not tox_cmd:
                raise ToxReaderError(
                    "Cannot fetch tox data. A 'tox' command was not found."
                )
            return (tox_cmd,)
        else:
            return (sys.executable, "-m", "tox")

    @functools.cached_property
    def _tox_version(self) -> t.Literal[3, 4]:
        """
        Check that the 'tox' command is a supported version and return it.

        Any unexpected outputs will raise an error, which allows for a cleaner early
        abort.
        """
        tox_version_proc = subprocess.run(
            [*self._tox_cmd, "--version"], text=True, capture_output=True
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

    @functools.cached_property
    def _tox_listenvs(self) -> tuple[str, ...]:
        output = subprocess.check_output([*self._tox_cmd, "--listenvs"], text=True)
        return tuple(line for line in output.splitlines() if line)

    def list_python_versions(self) -> list[str]:
        versions = set()
        for envname in self._tox_listenvs:
            for part in envname.split("-"):
                if match := re.match(r"py(\d)\.?(\d+)", part):
                    versions.add(match.group(1) + "." + match.group(2))
        return list(versions)
