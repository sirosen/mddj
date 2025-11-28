from __future__ import annotations

import functools
import pathlib
import typing as t

import click

from mddj._internal._compat import metadata
from mddj.api import DJ

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


class CommandState:
    def __init__(self) -> None:
        self.dj = DJ()

    @functools.cached_property
    def pyproject_path(self) -> pathlib.Path:
        return self.dj.pyproject_path

    @functools.cached_property
    def isolated_builds(self) -> bool:
        return self.dj.config.isolated_builds

    @functools.cached_property
    def build_capture(self) -> bool:
        return self.dj.config.capture_build_output

    def read_metadata(self) -> metadata.PackageMetadata:
        return self.dj.read._wheel_metadata


def common_args(cmd: F) -> F:
    @functools.wraps(cmd)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        state = click.get_current_context().ensure_object(CommandState)
        return cmd(*args, state=state, **kwargs)

    wrapper = click.help_option("-h", "--help")(wrapper)
    return t.cast(F, wrapper)
