import click

from mddj._cli.state import CommandState, common_args


@click.command("name")
@common_args
def read_name(*, state: CommandState) -> None:
    """Read the name of the current project."""
    click.echo(state.dj.read.name())
