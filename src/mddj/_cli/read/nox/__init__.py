import click

from mddj._cli.state import CommandState, common_args

from .list_versions import nox_list_versions
from .min_version import nox_min_version


@click.group("nox")
@common_args
def read_nox(*, state: CommandState) -> None:
    """Read metadata from the current project via 'nox'."""


read_nox.add_command(nox_list_versions)
read_nox.add_command(nox_min_version)
