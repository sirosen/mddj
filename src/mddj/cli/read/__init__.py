import click

from mddj.cli.state import CommandState, common_args

from .requires_python import read_requires_python
from .tox import read_tox
from .version import read_version


@click.group("read")
@common_args
def read(*, state: CommandState) -> None:
    """Read metadata from the current project."""


read.add_command(read_requires_python)
read.add_command(read_version)
read.add_command(read_tox)
