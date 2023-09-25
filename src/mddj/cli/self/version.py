from importlib.metadata import version

import click

from mddj.cli.state import CommandState, common_args


@click.command("version")
@common_args
def self_version(*, state: CommandState) -> None:
    """Get the version of mddj."""
    click.echo("mddj version: " + version("mddj"))
