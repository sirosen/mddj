import click

from mddj.cli.state import CommandState, common_args

from .list_versions import tox_list_versions
from .min_version import tox_min_version


@click.group("tox")
@common_args
def read_tox(*, state: CommandState) -> None:
    """Read metadata from the current project via 'tox'."""


read_tox.add_command(tox_min_version)
read_tox.add_command(tox_list_versions)
