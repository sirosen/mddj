import functools
import os
import typing as t

import click

from mddj.readers import get_wheel_metadata

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


class CommandState:
    def __init__(self) -> None:
        self.source_dir = os.getcwd()

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

    def read_metadata(self) -> dict[str, str]:
        return get_wheel_metadata(
            self.source_dir, isolated=self.isolated_builds, quiet=self.build_capture
        )


def common_args(cmd: F) -> F:
    @functools.wraps(cmd)
    def wrapper(*args, **kwargs) -> t.Any:
        state = click.get_current_context().ensure_object(CommandState)
        return cmd(*args, state=state, **kwargs)

    wrapper = click.help_option("-h", "--help")(wrapper)
    return t.cast(F, wrapper)
