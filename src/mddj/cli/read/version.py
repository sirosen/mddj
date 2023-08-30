import click

from mddj.cli.state import CommandState, common_args


@click.command("version")
@common_args
def read_version(*, state: CommandState) -> None:
    """Read the 'Version' of the current project."""
    data = state.read_metadata()
    click.echo(data.get("Version"))
