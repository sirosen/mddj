import click

from mddj._cli.error_handling import handle_mddj_errors
from mddj._cli.state import CommandState, common_args


@click.command("min-version")
@common_args
@handle_mddj_errors()
def nox_min_version(*, state: CommandState) -> None:
    """Print the minimum version of python tested under nox."""
    click.echo(state.dj.read.nox.min_python_version())
