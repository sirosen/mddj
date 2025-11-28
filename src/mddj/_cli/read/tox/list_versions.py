import click
from packaging.version import Version

from mddj._cli.state import CommandState, common_args


@click.command("list-versions")
@common_args
def tox_list_versions(*, state: CommandState) -> None:
    """Print all of the python versions tested under tox in version-sorted order."""
    versions = state.dj.read.tox.list_python_versions()
    for v in sorted(Version(v) for v in versions):
        click.echo(str(v))
