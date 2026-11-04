import click

from mddj._cli.state import CommandState, common_args

from .requires_python import write_requires_python
from .version import write_version


@click.group("write")
@common_args
def write(*, state: CommandState) -> None:
    """Write metadata for the current project."""


write.add_command(write_requires_python)
write.add_command(write_version)
