from __future__ import annotations

import functools
import typing as t

import click

from ..api import DJ

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


class CommandState:
    def __init__(self) -> None:
        self.dj = DJ()


def common_args(cmd: F) -> F:
    @functools.wraps(cmd)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        state = click.get_current_context().ensure_object(CommandState)
        return cmd(*args, state=state, **kwargs)

    wrapper = click.help_option("-h", "--help")(wrapper)
    return t.cast(F, wrapper)
