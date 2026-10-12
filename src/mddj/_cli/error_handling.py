import contextlib
import textwrap
import typing as t

import click

from mddj.api import MDDJError


@contextlib.contextmanager
def handle_mddj_errors() -> t.Iterator[None]:
    try:
        yield
    except MDDJError as err:
        click.echo(f"{type(err).__name__}: {err}", err=True)
        if hasattr(err, "__notes__"):
            for note in err.__notes__:
                click.echo(textwrap.indent(note, "    "), err=True)
        click.get_current_context().exit(1)
