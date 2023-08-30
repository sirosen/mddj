from __future__ import annotations

import functools
import os
import pathlib
import typing as t

import click

from mddj._compat import metadata
from mddj.config import ConfigData, read_config
from mddj.readers import get_wheel_metadata

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


class CommandState:
    def __init__(self) -> None:
        self.source_dir = pathlib.Path.cwd()

    @functools.cached_property
    def isolated_builds(self) -> bool:
        if (var := os.environ.get("MDDJ_ISOLATED_BUILDS")) is not None:
            return not (var.lower() in ("0", "false"))
        return True

    @functools.cached_property
    def build_capture(self) -> bool:
        # NB: this value currently does nothing
        # after a future 'build' release, it will control the output capturing
        # mode of the implicit 'build'
        if (var := os.environ.get("MDDJ_CAPTURE_BUILD_OUTPUT")) is not None:
            return not (var.lower() in ("0", "false"))
        return True

    def read_metadata(self) -> metadata.PackageMetadata:
        return get_wheel_metadata(
            self.source_dir, isolated=self.isolated_builds, quiet=self.build_capture
        )

    def read_config(self) -> ConfigData:
        return read_config(self.source_dir / "pyproject.toml")


def common_args(cmd: F) -> F:
    @functools.wraps(cmd)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        state = click.get_current_context().ensure_object(CommandState)
        return cmd(*args, state=state, **kwargs)

    wrapper = click.help_option("-h", "--help")(wrapper)
    return t.cast(F, wrapper)
