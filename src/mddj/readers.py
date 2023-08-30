from __future__ import annotations

import pathlib

import build.util

from mddj._compat import metadata


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
