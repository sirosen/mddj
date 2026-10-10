import click
from packaging.version import Version

from mddj._cli.state import CommandState, common_args


@click.command("list-versions")
@common_args
def nox_list_versions(*, state: CommandState) -> None:
    """Print all of the python versions tested under nox in version-sorted order."""
    versions = state.dj.read.nox.list_python_versions()
    if not versions:
        click.echo("Warning: no python versions detected from noxfile.", err=True)
    for v in sorted(Version(v) for v in versions):
        click.echo(str(v))
