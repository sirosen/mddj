from __future__ import annotations

import functools
import re
import shutil
import subprocess
import sys


class ToxReaderError(RuntimeError):
    """The class of errors which can be raised if ``tox`` data discovery fails."""


class ToxReader:
    """
    A ToxReader is a specialized data reader for ``tox`` data.

    Typically, users should simply create a DJ and then access the tox reader built by
    it, as in:

    .. code-block:: pycon

        >>> from mddj.api import DJ
        >>> dj = DJ()
        >>> dj.read.tox.list_versions()
        ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13']
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
    def _tox_version(self) -> str:
        tox_version_proc = subprocess.run(
            [*self._tox_cmd, "--version"], text=True, capture_output=True
        )
        if tox_version_proc.returncode != 0:
            raise ToxReaderError("Cannot fetch tox data. 'tox --version' failed.")

        return tox_version_proc.stdout.strip().partition(" ")[0]

    def _check_tox_version(self) -> str:
        """
        Check that the 'tox' command is a supported version and return it.

        Any unexpected outputs will raise an error, which allows for a cleaner early
        abort.
        """
        from packaging.version import Version

        version = Version(self._tox_version)
        if version.major in (3, 4):
            return self._tox_version
        else:
            raise ToxReaderError("'tox --version' was not a recognized version.")

    @functools.cached_property
    def _tox_listenvs(self) -> tuple[str, ...]:
        self._check_tox_version()
        output = subprocess.check_output([*self._tox_cmd, "--listenvs"], text=True)
        return tuple(line for line in output.splitlines() if line)

    def list_python_versions(self) -> list[str]:
        """List the Python versions which appear in the list of tox environments."""
        versions = set()
        for envname in self._tox_listenvs:
            for part in envname.split("-"):
                if match := re.match(r"py(\d)\.?(\d+)", part):
                    versions.add(match.group(1) + "." + match.group(2))
        return list(versions)
