import click

from mddj._cli.state import CommandState, common_args

from .dependencies import read_dependencies
from .description import read_description
from .import_names import read_import_names
from .import_namespaces import read_import_namespaces
from .keywords import read_keywords
from .name import read_name
from .requires_python import read_requires_python
from .tox import read_tox
from .version import read_version


@click.group("read")
@common_args
def read(*, state: CommandState) -> None:
    """Read metadata from the current project."""


read.add_command(read_dependencies)
read.add_command(read_description)
read.add_command(read_import_names)
read.add_command(read_import_namespaces)
read.add_command(read_keywords)
read.add_command(read_name)
read.add_command(read_requires_python)
read.add_command(read_version)

read.add_command(read_tox)
