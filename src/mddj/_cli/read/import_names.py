import click

from mddj._cli.state import CommandState, common_args


@click.command("import-names")
@common_args
def read_import_names(*, state: CommandState) -> None:
    """Read the Import-Names of the current project."""
    for n in state.dj.read.import_names():
        click.echo(n)
