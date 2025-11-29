import click

from mddj._cli.state import CommandState, common_args


@click.command("min-version")
@common_args
def tox_min_version(*, state: CommandState) -> None:
    """Print the minimum version of python tested under tox."""
    try:
        click.echo(state.dj.read.tox.min_python_version())
    except LookupError as e:
        click.echo(str(e), err=True)
        click.get_current_context().exit(1)
