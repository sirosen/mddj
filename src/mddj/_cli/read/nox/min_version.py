import textwrap

import click

from mddj._cli.state import CommandState, common_args
from mddj.api.reader.nox import NoxReaderError


@click.command("min-version")
@common_args
def nox_min_version(*, state: CommandState) -> None:
    """Print the minimum version of python tested under nox."""
    try:
        click.echo(state.dj.read.nox.min_python_version())
    except LookupError as e:
        click.echo(str(e), err=True)
        click.get_current_context().exit(1)
    except NoxReaderError as e:
        click.echo(f"NoxReaderError: {e}", err=True)
        if hasattr(e, "__notes__"):
            for note in e.__notes__:
                click.echo(textwrap.indent(note, "    "), err=True)
        click.get_current_context().exit(1)
