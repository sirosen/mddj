import click

from mddj._cli.state import CommandState, common_args


@click.command("import-namespaces")
@common_args
def read_import_namespaces(*, state: CommandState) -> None:
    """Read the Import-Namespaces of the current project."""
    for n in state.dj.read.import_namespaces():
        click.echo(n)
