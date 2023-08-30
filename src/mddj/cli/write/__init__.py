import click

from mddj.cli.state import CommandState, common_args

from .version import write_version


@click.group("write")
@common_args
def write(*, state: CommandState) -> None:
    """Write metadata for the current project."""


write.add_command(write_version)
