from __future__ import annotations

import os as _os
import platform as _platform
import sys as _sys

from ..._internal import _cached_methods


class SystemInfoReader:
    """
    This is a simple reader of Python's system introspection modules.

    The method names intentionally match the names used in the marker specification
    whenever applicable/possible.
    """

    def implementation_name(self) -> str:
        return _sys.implementation.name

    @_cached_methods.cached_method
    def implementation_version(self) -> str:
        info = _sys.implementation.version
        if info.releaselevel == "final":
            return f"{info.major}.{info.minor}.{info.micro}"

        tag = info.releaselevel[0]
        return f"{info.major}.{info.minor}.{info.micro}{tag}{info.serial}"

    def os_name(self) -> str:
        return _os.name

    def platform_machine(self) -> str:
        return _platform.machine()

    def platform_release(self) -> str:
        return _platform.release()

    def platform_system(self) -> str:
        return _platform.system()

    def platform_version(self) -> str:
        return _platform.version()

    def platform_python_implementation(self) -> str:
        return _platform.python_implementation()

    def python_full_version(self) -> str:
        return _platform.python_version()

    def python_version(self) -> str:
        major, minor, _patch = _platform.python_version_tuple()
        return f"{major}.{minor}"

    def sys_platform(self) -> str:
        return _sys.platform
