import click

from mddj._cli.state import CommandState, common_args


@click.command("dependencies")
@common_args
def read_dependencies(*, state: CommandState) -> None:
    """Read the dependencies of the current project."""
    for d in state.dj.read.dependencies():
        click.echo(d)
