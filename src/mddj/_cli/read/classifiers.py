import click

from mddj._cli.state import CommandState, common_args


@click.command("classifiers")
@common_args
def read_classifiers(*, state: CommandState) -> None:
    """Read the classifiers of the current project."""
    for c in state.dj.read.classifiers():
        click.echo(c)
