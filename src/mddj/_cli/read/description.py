import click

from mddj._cli.state import CommandState, common_args


@click.command("description")
@common_args
def read_description(*, state: CommandState) -> None:
    """Read the description of the current project."""
    click.echo(state.dj.read.description())
