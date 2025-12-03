import click

from mddj._cli.state import CommandState, common_args


@click.command("keywords")
@common_args
def read_keywords(*, state: CommandState) -> None:
    """Read the keywords of the current project."""
    for d in state.dj.read.keywords():
        click.echo(d)
