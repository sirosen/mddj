import click

from .requires_python import read_requires_python
from .version import read_version


@click.group("read")
@click.help_option("-h", "--help")
def read() -> None:
    """Read metadata from the current project."""


read.add_command(read_requires_python)
read.add_command(read_version)
